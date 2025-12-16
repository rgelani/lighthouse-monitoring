from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session, engine
from typing import List
from datetime import datetime

from .database import get_db
from . import models, schemas

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Metrics Service",
    version="1.0.0",
    description="Collects and stores metrics from monitored services"
)

@app.get("/")
async def root():
    """Service information"""
    return {
        "service": "metrics-service",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health", response_model=schemas.HealthResponse)
async def health(db: Session = Depends(get_db)):
    """Health check with database connectivity"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_connected = True
    except Exception:
        db_connected = False

    return {
        "status": "healthy" if db_connected else "degraded",
        "timestamp": datetime.utcnow(),
        "database_connected": db_connected
    }    

@app.post("/metrics", response_model=schemas.MetricResponse, status_code=status.HTTP_201_CREATED)
async def create_metric(metric: schemas.MetriCreate, db: Session = Depends(get_db)):
    """Create a new metric entry"""
    db_metric = models.ServiceMetric(
        service_name = metric.service_name,
        metric_type = metric.metric_type,
        value = metric.value,
        unit = metric.unit,
        extra_data = metric.extra_data
    )
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric

@app.get("/metrics", response_model=List[schemas.MetricResponse])
async def get_metrics(
    service_name: str = None,
    metric_type: str = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get metrics with optional filtering"""
    query = db.query(models.ServiceMetric)
    
    if service_name:
        query = query.filter(models.ServiceMetric.service_name == service_name)
    if metric_type:
        query = query.filter(models.ServiceMetric.metric_type == metric_type)
    
    metrics = query.order_by(models.ServiceMetric.timestamp.desc()).limit(limit).all()
    return metrics


@app.post("/services", response_model=schemas.ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(service: schemas.ServiceCreate, db: Session = Depends(get_db)):
    """Register a new service"""
    # Check if service already exists
    existing = db.query(models.Service).filter(models.Service.name == service.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Service '{service.name}' already exists"
        )
    
    db_service = models.Service(
        name=service.name,
        description=service.description,
        url=service.url
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service


@app.get("/services", response_model=List[schemas.ServiceResponse])
async def get_services(db: Session = Depends(get_db)):
    """Get all registered services"""
    services = db.query(models.Service).all()
    return services