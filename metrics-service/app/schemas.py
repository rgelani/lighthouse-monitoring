from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class MetriCreate(BaseModel):
    """Schema for creating a metric"""
    service_name: str = Field(..., min_length=1, max_length=100)
    metric_type: str = Field(..., min_length=1, max_length=50)
    value: float = Field(..., ge=0)
    unit: str = Field(..., min_length=1, max_length=20)
    extra_data: Optional[Dict[str, Any]] = None

class MetricResponse(BaseModel):   
    """Schema for metric response"""
    id: int
    service_name: str
    metric_type: str
    value: float
    unit: str
    extra_data:Optional[Dict[str, Any]]
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

class ServiceCreate(BaseModel):
    """Schema for creating a service"""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    url: Optional[str] = None        

class ServiceResponse(BaseModel):
    """Schema for service response"""
    id: int
    name: str
    description: Optional[str]
    url: Optional[str]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

class HealthResponse(BaseModel):
    """Schema for health check response"""
    status: str
    timestamp: datetime
    database_connected: bool        




