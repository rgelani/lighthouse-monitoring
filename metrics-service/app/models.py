from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func 
from datetime import datetime
from .database import Base

class ServiceMetric(Base):
    """Store metrics for monitored services"""
    __tablename__ = "service_metrics"

    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String, index=True, nullable=False)
    metric_type = Column(String, nullable=False) # cpu, memory, disk, network
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False) # percent, bytes, etc
    extra_data = Column(JSON, nullable=True) # Additional context
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<ServiceMetric(service={self.service_name}, type={self.metric_type}, value={self.value})>"
    
class Service(Base):
    """Store registered services"""

    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    url = Column(String, nullable=True)
    status = Column(String, default="active") #active, inactive, error
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Service(name={self.name}, status={self.status})>"


