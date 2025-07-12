import pytest
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app
from utils.database import get_db

@pytest.fixture
def app():
    """Create and configure a test app"""
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()

@pytest.fixture(autouse=True)
def clean_database(app):
    """Clean up database before each test"""
    with app.app_context():
        db = get_db()
        if db is not None:
            db.datasets.drop()
            db.quality_logs.drop()
    yield
    with app.app_context():
        db = get_db()
        if db is not None:
            db.datasets.drop()
            db.quality_logs.drop()

@pytest.fixture
def sample_dataset(client):
    """Create a sample dataset for testing quality logs"""
    dataset_data = {
        "name": "Test Dataset for Quality",
        "owner": "test_user",
        "description": "Dataset for quality log testing",
        "tags": ["test", "quality"]
    }
    
    response = client.post('/datasets',
                         data=json.dumps(dataset_data),
                         content_type='application/json')
    
    return json.loads(response.data)['data']['id']

class TestQualityLogs:
    def test_create_quality_log_success(self, client, sample_dataset):
        """Test successful quality log creation"""
        log_data = {
            "status": "PASS",
            "details": "All quality checks passed successfully"
        }
        
        response = client.post(f'/datasets/{sample_dataset}/quality-logs',
                             data=json.dumps(log_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Quality log created successfully'
        assert data['data']['status'] == 'PASS'
        assert data['data']['details'] == log_data['details']

    def test_create_quality_log_invalid_status(self, client, sample_dataset):
        """Test quality log creation with invalid status"""
        log_data = {
            "status": "INVALID_STATUS",
            "details": "This should fail"
        }
        
        response = client.post(f'/datasets/{sample_dataset}/quality-logs',
                             data=json.dumps(log_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Validation error' in data['error']

    def test_create_quality_log_nonexistent_dataset(self, client):
        """Test quality log creation for non-existent dataset"""
        fake_id = "507f1f77bcf86cd799439011" 
        log_data = {
            "status": "PASS",
            "details": "This should fail"
        }
        
        response = client.post(f'/datasets/{fake_id}/quality-logs',
                             data=json.dumps(log_data),
                             content_type='application/json')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'Dataset not found'

    def test_get_quality_logs(self, client, sample_dataset):
        """Test getting quality logs for a dataset"""
     
        log_data_1 = {"status": "PASS", "details": "First check passed"}
        log_data_2 = {"status": "FAIL", "details": "Second check failed"}
        
        client.post(f'/datasets/{sample_dataset}/quality-logs',
                   data=json.dumps(log_data_1),
                   content_type='application/json')
        
        client.post(f'/datasets/{sample_dataset}/quality-logs',
                   data=json.dumps(log_data_2),
                   content_type='application/json')
        
        response = client.get(f'/datasets/{sample_dataset}/quality-logs')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'data' in data
        assert 'logs' in data['data']
        assert len(data['data']['logs']) == 2

    def test_get_quality_summary(self, client, sample_dataset):
        """Test getting quality summary for a dataset"""
        pass_log = {"status": "PASS", "details": "Check passed"}
        fail_log = {"status": "FAIL", "details": "Check failed"}
        
        client.post(f'/datasets/{sample_dataset}/quality-logs',
                   data=json.dumps(pass_log),
                   content_type='application/json')
        
        client.post(f'/datasets/{sample_dataset}/quality-logs',
                   data=json.dumps(fail_log),
                   content_type='application/json')
        
        response = client.get(f'/datasets/{sample_dataset}/quality-summary')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        summary = data['data']
        
        assert summary['total_logs'] == 2
        assert summary['pass_count'] == 1
        assert summary['fail_count'] == 1
        assert summary['pass_rate'] == 50.0

    def test_get_latest_quality_status(self, client, sample_dataset):
        """Test getting latest quality status for a dataset"""
        log1 = {"status": "PASS", "details": "First check"}
        log2 = {"status": "FAIL", "details": "Latest check"}
        
        client.post(f'/datasets/{sample_dataset}/quality-logs',
                   data=json.dumps(log1),
                   content_type='application/json')
        
        client.post(f'/datasets/{sample_dataset}/quality-logs',
                   data=json.dumps(log2),
                   content_type='application/json')
        
        response = client.get(f'/datasets/{sample_dataset}/quality-status')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['data']['status'] == 'FAIL'
        assert data['data']['details'] == 'Latest check'

    def test_get_quality_logs_pagination(self, client, sample_dataset):
        """Test quality logs pagination"""
        for i in range(5):
            log_data = {"status": "PASS", "details": f"Check {i+1}"}
            client.post(f'/datasets/{sample_dataset}/quality-logs',
                       data=json.dumps(log_data),
                       content_type='application/json')
        
 
        response = client.get(f'/datasets/{sample_dataset}/quality-logs?page=1&limit=3')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['data']['total'] == 5
        assert len(data['data']['logs']) == 3
        assert data['data']['page'] == 1
        assert data['data']['total_pages'] == 2
