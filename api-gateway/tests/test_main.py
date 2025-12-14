import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAPIGateway:
    def test_root_endpoint(self):
        """Test root endpoint returns correct structure"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "api-gateway"
        assert data["version"] == "1.0.0"
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_health_endpoint(self):
        """Test health check returns system metrics"""    
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "system" in data
        assert "cpu_percent" in data["system"]
        assert "memory_percent" in data["system"]
        assert data["system"]["cpu_percent"] >= 0
        assert data["system"]["memory_percent"] >= 0

    def test_metrics_endpoint(self):
        """Test metrics endpoint returns detailed info"""    
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "cpu" in data
        assert "memory" in data
        assert "timestamp" in data
        assert data["cpu"]["cpu_count"] > 0
        assert data["memory"]["total_gb"] > 0

    def test_health_endpoint_structure(self):
        """Test health endpoint has all required fields"""    
        response = client.get("/health")
        data = response.json()
        required_fields = ["status", "timestamp", "system"]
        for field in required_fields:
            assert field in data

        system_fields = ["cpu_percent", "memory_percent", "memory_available_mb", "disk_percent"]
        for field in system_fields:
            assert field in data["system"]    

    def test_metrics_cpu_structure(self):
        """Test metrics CPU data structure"""      
        response = client.get("/metrics")   
        data = response.json()
        assert "cpu_count" in data["cpu"]
        assert "percent" in data["cpu"]
        assert data["cpu"]["cpu_count"] > 0
        assert 0 <= data["cpu"]["percent"] <= 100

    def test_metrics_memory_structure(self):
        """Test metrics memory data structure"""   
        response = client.get("/metrics")
        data = response.json()
        memory_fields = ["total_gb", "available_gb", "used_gb", "percent"] 
        for field in memory_fields:
            assert field in data["memory"]

        assert data["memory"]["total_gb"] > 0    
        assert data["memory"]["used_gb"] >= 0
        assert data["memory"]["available_gb"] >= 0