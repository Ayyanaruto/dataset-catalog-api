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
def sample_dataset():
    """Sample dataset data for testing"""
    return {
        "name": "Test Dataset",
        "owner": "test_user",
        "description": "A test dataset",
        "tags": ["test", "sample"]
    }

class TestDatasets:
    def test_create_dataset_success(self, client, sample_dataset):
        """Test successful dataset creation"""
        response = client.post('/datasets', 
                             data=json.dumps(sample_dataset),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Dataset created successfully'
        assert data['data']['name'] == sample_dataset['name']
        assert data['data']['owner'] == sample_dataset['owner']
        assert 'id' in data['data']

    def test_create_dataset_missing_required_fields(self, client):
        """Test dataset creation with missing required fields"""
        incomplete_dataset = {"name": "Test Dataset"}
        
        response = client.post('/datasets',
                             data=json.dumps(incomplete_dataset),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Validation error' in data['error']

    def test_get_datasets(self, client, sample_dataset):
        """Test getting datasets list"""
      
        client.post('/datasets',
                   data=json.dumps(sample_dataset),
                   content_type='application/json')
        
        response = client.get('/datasets')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'data' in data
        assert 'datasets' in data['data']
        assert len(data['data']['datasets']) > 0

    def test_get_dataset_by_id(self, client, sample_dataset):
        """Test getting a specific dataset by ID"""
      
        create_response = client.post('/datasets',
                                    data=json.dumps(sample_dataset),
                                    content_type='application/json')
        
        created_data = json.loads(create_response.data)
        dataset_id = created_data['data']['id']
        
      
        response = client.get(f'/datasets/{dataset_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['name'] == sample_dataset['name']

    def test_get_nonexistent_dataset(self, client):
        """Test getting a non-existent dataset"""
        fake_id = "507f1f77bcf86cd799439011"  
        response = client.get(f'/datasets/{fake_id}')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'Dataset not found'

    def test_update_dataset(self, client, sample_dataset):
        """Test updating a dataset"""
        create_response = client.post('/datasets',
                                    data=json.dumps(sample_dataset),
                                    content_type='application/json')
        
        created_data = json.loads(create_response.data)
        dataset_id = created_data['data']['id']
        
        update_data = {"description": "Updated description"}
        response = client.put(f'/datasets/{dataset_id}',
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['description'] == "Updated description"

    def test_delete_dataset(self, client, sample_dataset):
        """Test soft deleting a dataset"""
        create_response = client.post('/datasets',
                                    data=json.dumps(sample_dataset),
                                    content_type='application/json')
        
        created_data = json.loads(create_response.data)
        dataset_id = created_data['data']['id']
        
        response = client.delete(f'/datasets/{dataset_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Dataset deleted successfully'
        
        get_response = client.get(f'/datasets/{dataset_id}')
        assert get_response.status_code == 404

    def test_dataset_filtering_by_owner(self, client):
        """Test filtering datasets by owner"""
        dataset1 = {"name": "Dataset 1", "owner": "user1", "tags": ["test"]}
        dataset2 = {"name": "Dataset 2", "owner": "user2", "tags": ["test"]}
        
        client.post('/datasets', data=json.dumps(dataset1), content_type='application/json')
        client.post('/datasets', data=json.dumps(dataset2), content_type='application/json')
        
        response = client.get('/datasets?owner=user1')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        datasets = data['data']['datasets']
        
        for dataset in datasets:
            assert dataset['owner'] == 'user1'

    def test_dataset_filtering_by_tag(self, client):
        """Test filtering datasets by tag"""
        dataset1 = {"name": "Dataset 1", "owner": "user1", "tags": ["production"]}
        dataset2 = {"name": "Dataset 2", "owner": "user1", "tags": ["test"]}
        
        client.post('/datasets', data=json.dumps(dataset1), content_type='application/json')
        client.post('/datasets', data=json.dumps(dataset2), content_type='application/json')
        
        
        response = client.get('/datasets?tag=production')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        datasets = data['data']['datasets']
        
        for dataset in datasets:
            assert 'production' in dataset['tags']
