import pytest
from datetime import datetime


class TestMetricsService:
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns correct structure"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "metrics-service"
        assert data["version"] == "1.0.0"
        assert data["status"] == "healthy"
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert "database_connected" in data
        assert isinstance(data["database_connected"], bool)
    
    def test_create_metric(self, client):
        """Test creating a metric"""
        metric_data = {
            "service_name": "api-gateway",
            "metric_type": "cpu",
            "value": 45.5,
            "unit": "percent",
            "extra_data": {"host": "server-01"}
        }
        response = client.post("/metrics", json=metric_data)
        assert response.status_code == 201
        data = response.json()
        assert data["service_name"] == "api-gateway"
        assert data["metric_type"] == "cpu"
        assert data["value"] == 45.5
        assert data["unit"] == "percent"
        assert "id" in data
        assert "timestamp" in data
    
    def test_create_metric_validation(self, client):
        """Test metric validation"""
        # Missing required field
        invalid_data = {
            "service_name": "api-gateway",
            "metric_type": "cpu"
            # Missing: value, unit
        }
        response = client.post("/metrics", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_get_metrics(self, client):
        """Test retrieving metrics"""
        # Create test metrics
        metric1 = {
            "service_name": "api-gateway",
            "metric_type": "cpu",
            "value": 45.5,
            "unit": "percent"
        }
        metric2 = {
            "service_name": "worker",
            "metric_type": "memory",
            "value": 1024.0,
            "unit": "MB"
        }
        client.post("/metrics", json=metric1)
        client.post("/metrics", json=metric2)
        
        # Get all metrics
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_get_metrics_filtered_by_service(self, client):
        """Test filtering metrics by service name"""
        # Create metrics for different services
        client.post("/metrics", json={
            "service_name": "api-gateway",
            "metric_type": "cpu",
            "value": 45.5,
            "unit": "percent"
        })
        client.post("/metrics", json={
            "service_name": "worker",
            "metric_type": "cpu",
            "value": 60.0,
            "unit": "percent"
        })
        
        # Filter by service
        response = client.get("/metrics?service_name=api-gateway")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["service_name"] == "api-gateway"
    
    def test_get_metrics_filtered_by_type(self, client):
        """Test filtering metrics by type"""
        # Create metrics of different types
        client.post("/metrics", json={
            "service_name": "api-gateway",
            "metric_type": "cpu",
            "value": 45.5,
            "unit": "percent"
        })
        client.post("/metrics", json={
            "service_name": "api-gateway",
            "metric_type": "memory",
            "value": 2048.0,
            "unit": "MB"
        })
        
        # Filter by type
        response = client.get("/metrics?metric_type=cpu")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["metric_type"] == "cpu"
    
    def test_create_service(self, client):
        """Test creating a service"""
        service_data = {
            "name": "api-gateway",
            "description": "Main API gateway",
            "url": "http://api-gateway:8000"
        }
        response = client.post("/services", json=service_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "api-gateway"
        assert data["description"] == "Main API gateway"
        assert data["status"] == "active"
        assert "id" in data
    
    def test_create_duplicate_service(self, client):
        """Test creating duplicate service fails"""
        service_data = {
            "name": "api-gateway",
            "description": "Main API gateway"
        }
        # Create first service
        response1 = client.post("/services", json=service_data)
        assert response1.status_code == 201
        
        # Try to create duplicate
        response2 = client.post("/services", json=service_data)
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"]
    
    def test_get_services(self, client):
        """Test retrieving services"""
        # Create test services
        client.post("/services", json={
            "name": "api-gateway",
            "description": "API Gateway"
        })
        client.post("/services", json={
            "name": "worker",
            "description": "Background Worker"
        })
        
        # Get all services
        response = client.get("/services")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        service_names = [s["name"] for s in data]
        assert "api-gateway" in service_names
        assert "worker" in service_names