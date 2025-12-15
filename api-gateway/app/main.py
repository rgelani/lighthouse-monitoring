from fastapi import FastAPI, HTTPException
from datetime import datetime
import psutil
import os
import platform

app = FastAPI(
    title="API Gateway",
    version="1.0.0",
    description="Main entry point for Lighthouse monitoring platform",
)


@app.get("/")
async def root():
    """Service information endpoint"""
    return {
        "service": "api-gateway",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
    }


@app.get("/health")
async def health():
    """Health check endpoint with system metrics"""
    try:
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "cpu_percent": cpu,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available / (1024 * 1024),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024 * 1024 * 1024),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.get("/metrics")
async def metrics():
    print("METRICS VERSION 2 LOADED")

    """Detail system metrics"""
    try:
        cpu_count = psutil.cpu_count()
        memory = psutil.virtual_memory()

        # Try to get CPU frequency, but handle Apple Silicon gracefully
        frequency = None
        if platform.system() != "Darwin":
            try:
                cpu_freq = psutil.cpu_freq()
                if cpu_freq:
                    frequency = cpu_freq.current
            except (AttributeError, FileNotFoundError, OSError):
                # Apple Silicon doesn't expose CPU frequency via sysctl
                pass

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": {
                "cpu_count": cpu_count,
                "percent": psutil.cpu_percent(interval=1),
                "frequency_mhz": frequency,
            },
            "memory": {
                "total_gb": memory.total / (1024**3),
                "available_gb": memory.available / (1024**3),
                "used_gb": memory.used / (1024**3),
                "percent": memory.percent,
            },
            "uptime_seconds": int(psutil.boot_time()),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Metrics collection failed: {str(e)}"
        )
