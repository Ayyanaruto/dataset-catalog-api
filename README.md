# Dataset Catalog API

A lightweight backend API built with Python, Flask, and MongoDB for The API will be available at `http://localhost:5000`

## Docker Setup (Recommended)

The easiest way to run the Dataset Catalog API is using Docker. This approach automatically sets up both the API and MongoDB database.

### Prerequisites

- Docker
- Docker Compose

### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd dataset-catalog-api
   ```

2. **Create environment file** (optional)
   ```bash
   cp .env.example .env
   # Edit .env file with your preferred settings
   ```

3. **Start the application**
   ```bash
   # Option 1: Using docker-compose directly
   docker-compose up -d                              # Development mode
   
   # Option 2: Using the management script
   ./docker-manage.sh start                          # Development mode
   
   # Option 3: Using Makefile
   make start                                        # Development mode
   ```

4. **Access the services**
   - API: http://localhost:5000
   - API Documentation: http://localhost:5000/apidocs  
   - MongoDB Admin (dev only): http://localhost:8081 (admin/admin123)

### Docker Commands

```bash
# Using docker-compose directly
docker-compose up -d                    # Start services
docker-compose down                     # Stop services
docker-compose logs -f                  # View logs
docker-compose logs -f api              # View API logs only
docker-compose up -d --build            # Rebuild and restart
docker-compose down -v                  # Stop and remove everything

# Using the management script
./docker-manage.sh start                # Start development
./docker-manage.sh stop                 # Stop services
./docker-manage.sh logs                 # Show logs
./docker-manage.sh status               # Show container status
./docker-manage.sh clean                # Clean up everything
./docker-manage.sh help                 # Show help

# Using Makefile
make start                              # Start development
make stop                               # Stop services
make logs                               # Show logs
make status                             # Show container status
make clean                              # Clean up everything
make test                               # Run tests in Docker
make help                               # Show help
```


### Docker Services

- **API Service**: Python Flask application
- **MongoDB**: Database service with persistent volume
- **Mongo Express**: Web-based MongoDB admin interface

### API Documentation

Once the application is running, visit `http://localhost:5000/apidocs` to view the interactive Swagger documentation.ing datasets and tracking quality logs.

## Features

- **Dataset Management**: Create, read, update, and soft delete datasets
- **Quality Logging**: Track quality checks with PASS/FAIL status
- **Filtering & Pagination**: Filter datasets by owner/tags with pagination support
- **API Documentation**: Auto-generated Swagger documentation
- **Data Validation**: Input validation using Pydantic models
- **Comprehensive Testing**: Unit tests with pytest

## Tech Stack

- **Backend**: Python 3.10+, Flask 2.x
- **Database**: MongoDB with PyMongo
- **Validation**: Pydantic
- **Documentation**: Flasgger (Swagger)
- **Testing**: pytest
- **CORS**: Flask-CORS

## Project Structure

\`\`\`
dataset-catalog-api/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── README.md            # Project documentation
├── models/              # Pydantic data models
│   ├── dataset.py
│   └── quality_log.py
├── routes/              # API route handlers
│   ├── datasets.py
│   └── quality_logs.py
├── services/            # Business logic layer
│   ├── dataset_service.py
│   └── quality_log_service.py
├── utils/               # Utility functions
│   ├── database.py
│   └── helpers.py
└── tests/               # Test files
    ├── test_datasets.py
    └── test_quality_logs.py
\`\`\`

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- MongoDB (local installation or MongoDB Atlas)
- pip (Python package manager)

### Installation

1. **Clone the repository**
   \`\`\`bash
   git clone <repository-url>
   cd dataset-catalog-api
   \`\`\`

2. **Create a virtual environment**
   \`\`\`bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   \`\`\`

3. **Install dependencies**
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

4. **Set up environment variables** (optional)
   Create a \`.env\` file in the root directory:
   \`\`\`
   MONGODB_URI=mongodb://localhost:27017/
   MONGODB_DB=dataset_catalog
   SECRET_KEY=your-secret-key-here
   FLASK_DEBUG=True
   \`\`\`

5. **Start MongoDB**
   Make sure MongoDB is running on your system or configure connection to MongoDB Atlas.

6. **Run the application**
   \`\`\`bash
   python app.py
   \`\`\`

The API will be available at \`http://localhost:5000\`

### API Documentation

Once the application is running, visit \`http://localhost:5000/apidocs\` to view the interactive Swagger documentation.

## API Endpoints

### Datasets

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | \`/datasets\` | Create a new dataset |
| GET | \`/datasets\` | List all datasets (with filtering) |
| GET | \`/datasets/<id>\` | Get dataset details |
| PUT | \`/datasets/<id>\` | Update a dataset |
| DELETE | \`/datasets/<id>\` | Soft delete a dataset |
| GET | \`/datasets/stats\` | Get dataset statistics |

### Quality Logs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | \`/datasets/<id>/quality-logs\` | Add a quality log |
| GET | \`/datasets/<id>/quality-logs\` | Get quality logs |
| GET | \`/datasets/<id>/quality-summary\` | Get quality summary |
| GET | \`/datasets/<id>/quality-status\` | Get latest quality status |

## Example API Requests

### Create a Dataset

\`\`\`bash
curl -X POST http://localhost:5000/datasets \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "Customer Data 2024",
    "owner": "john.doe",
    "description": "Customer dataset for 2024 analysis",
    "tags": ["customer", "2024", "analysis"]
  }'
\`\`\`

### Get All Datasets

\`\`\`bash
curl http://localhost:5000/datasets
\`\`\`

### Filter Datasets by Owner

\`\`\`bash
curl "http://localhost:5000/datasets?owner=john.doe&page=1&limit=10"
\`\`\`

### Get Dataset Details

\`\`\`bash
curl http://localhost:5000/datasets/64f8a1b2c3d4e5f6a7b8c9d0
\`\`\`

### Update a Dataset

\`\`\`bash
curl -X PUT http://localhost:5000/datasets/64f8a1b2c3d4e5f6a7b8c9d0 \\
  -H "Content-Type: application/json" \\
  -d '{
    "description": "Updated description",
    "tags": ["customer", "2024", "updated"]
  }'
\`\`\`

### Add Quality Log

\`\`\`bash
curl -X POST http://localhost:5000/datasets/64f8a1b2c3d4e5f6a7b8c9d0/quality-logs \\
  -H "Content-Type: application/json" \\
  -d '{
    "status": "PASS",
    "details": "All data quality checks passed successfully"
  }'
\`\`\`

### Get Quality Logs

\`\`\`bash
curl http://localhost:5000/datasets/64f8a1b2c3d4e5f6a7b8c9d0/quality-logs
\`\`\`

### Get Quality Summary

\`\`\`bash
curl http://localhost:5000/datasets/64f8a1b2c3d4e5f6a7b8c9d0/quality-summary
\`\`\`

## Running Tests

Run the test suite using pytest:

\`\`\`bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_datasets.py

# Run with coverage
pytest --cov=.
\`\`\`

## Database Schema

### Datasets Collection

\`\`\`json
{
  "_id": "ObjectId",
  "name": "string",
  "owner": "string", 
  "description": "string",
  "tags": ["string"],
  "created_at": "datetime",
  "updated_at": "datetime",
  "is_deleted": "boolean"
}
\`\`\`

### Quality Logs Collection

\`\`\`json
{
  "_id": "ObjectId",
  "dataset_id": "ObjectId",
  "status": "PASS|FAIL",
  "details": "string",
  "timestamp": "datetime"
}
\`\`\`

## Error Handling

The API returns standardized error responses:

\`\`\`json
{
  "error": "Error message description"
}
\`\`\`

Common HTTP status codes:
- \`200\`: Success
- \`201\`: Created
- \`400\`: Bad Request (validation errors)
- \`404\`: Not Found
- \`409\`: Conflict (duplicate data)
- \`500\`: Internal Server Error

## Development

### Adding New Features

1. Create models in \`models/\` directory
2. Implement business logic in \`services/\`
3. Add route handlers in \`routes/\`
4. Write tests in \`tests/\`
5. Update API documentation