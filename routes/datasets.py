from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from services.dataset_service import DatasetService
from models.dataset import DatasetCreate, DatasetUpdate
from utils.helpers import serialize_doc, validate_object_id, create_error_response, create_success_response

datasets_bp = Blueprint('datasets', __name__)

def get_dataset_service():
    return DatasetService()

@datasets_bp.route('/datasets', methods=['POST'])
def create_dataset():
    """
    Create a new dataset
    ---
    tags:
      - Datasets
    parameters:
      - in: body
        name: dataset
        description: Dataset data
        required: true
        schema:
          type: object
          required:
            - name
            - owner
          properties:
            name:
              type: string
              example: "Customer Data 2024"
            owner:
              type: string
              example: "john.doe"
            description:
              type: string
              example: "Customer dataset for 2024 analysis"
            tags:
              type: array
              items:
                type: string
              example: ["customer", "2024", "analysis"]
    responses:
      201:
        description: Dataset created successfully
      400:
        description: Invalid input data
      409:
        description: Dataset already exists
    """
    try:
        data = request.get_json()
        if not data:
            return create_error_response("Request body is required")
        
        dataset_data = DatasetCreate(**data)
        result = get_dataset_service().create_dataset(dataset_data)
        
        return create_success_response(
            serialize_doc(result),
            "Dataset created successfully",
            201
        )
        
    except ValidationError as e:
        return create_error_response(f"Validation error: {e}")
    except ValueError as e:
        return create_error_response(str(e), 409)
    except Exception as e:
        return create_error_response(f"Internal server error: {str(e)}", 500)

@datasets_bp.route('/datasets', methods=['GET'])
def get_datasets():
    """
    Get all datasets with optional filtering
    ---
    tags:
      - Datasets
    parameters:
      - in: query
        name: owner
        type: string
        description: Filter by owner
      - in: query
        name: tag
        type: string
        description: Filter by tag
      - in: query
        name: page
        type: integer
        default: 1
        description: Page number
      - in: query
        name: limit
        type: integer
        default: 20
        description: Items per page
    responses:
      200:
        description: List of datasets
    """
    try:
        owner = request.args.get('owner')
        tag = request.args.get('tag')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 20
        
        result = get_dataset_service().get_datasets(owner, tag, page, limit)
        result['datasets'] = serialize_doc(result['datasets'])
        
        return create_success_response(result)
        
    except ValueError as e:
        return create_error_response(f"Invalid parameter: {e}")
    except Exception as e:
        return create_error_response(f"Internal server error: {str(e)}", 500)

@datasets_bp.route('/datasets/<dataset_id>', methods=['GET'])
def get_dataset(dataset_id):
    """
    Get a specific dataset by ID
    ---
    tags:
      - Datasets
    parameters:
      - in: path
        name: dataset_id
        type: string
        required: true
        description: Dataset ID
    responses:
      200:
        description: Dataset details
      404:
        description: Dataset not found
    """
    try:
        if not validate_object_id(dataset_id):
            return create_error_response("Invalid dataset ID")
        
        dataset = get_dataset_service().get_dataset_by_id(dataset_id)
        if not dataset:
            return create_error_response("Dataset not found", 404)
        
        return create_success_response(serialize_doc(dataset))
        
    except Exception as e:
        return create_error_response(f"Internal server error: {str(e)}", 500)

@datasets_bp.route('/datasets/<dataset_id>', methods=['PUT'])
def update_dataset(dataset_id):
    """
    Update a dataset
    ---
    tags:
      - Datasets
    parameters:
      - in: path
        name: dataset_id
        type: string
        required: true
        description: Dataset ID
      - in: body
        name: dataset
        description: Dataset update data
        schema:
          type: object
          properties:
            name:
              type: string
            owner:
              type: string
            description:
              type: string
            tags:
              type: array
              items:
                type: string
    responses:
      200:
        description: Dataset updated successfully
      400:
        description: Invalid input data
      404:
        description: Dataset not found
    """
    try:
        if not validate_object_id(dataset_id):
            return create_error_response("Invalid dataset ID")
        
        data = request.get_json()
        if not data:
            return create_error_response("Request body is required")
        
        update_data = DatasetUpdate(**data)
        result = get_dataset_service().update_dataset(dataset_id, update_data)
        
        if not result:
            return create_error_response("Dataset not found", 404)
        
        return create_success_response(
            serialize_doc(result),
            "Dataset updated successfully"
        )
        
    except ValidationError as e:
        return create_error_response(f"Validation error: {e}")
    except ValueError as e:
        return create_error_response(str(e), 409)
    except Exception as e:
        return create_error_response(f"Internal server error: {str(e)}", 500)

@datasets_bp.route('/datasets/<dataset_id>', methods=['DELETE'])
def delete_dataset(dataset_id):
    """
    Soft delete a dataset
    ---
    tags:
      - Datasets
    parameters:
      - in: path
        name: dataset_id
        type: string
        required: true
        description: Dataset ID
    responses:
      200:
        description: Dataset deleted successfully
      404:
        description: Dataset not found
    """
    try:
        if not validate_object_id(dataset_id):
            return create_error_response("Invalid dataset ID")
        
        success = get_dataset_service().delete_dataset(dataset_id)
        if not success:
            return create_error_response("Dataset not found", 404)
        
        return create_success_response(
            {"deleted": True},
            "Dataset deleted successfully"
        )
        
    except Exception as e:
        return create_error_response(f"Internal server error: {str(e)}", 500)

@datasets_bp.route('/datasets/stats', methods=['GET'])
def get_dataset_stats():
    """
    Get dataset statistics
    ---
    tags:
      - Datasets
    responses:
      200:
        description: Dataset statistics
    """
    try:
        stats = get_dataset_service().get_dataset_stats()
        return create_success_response(stats)
        
    except Exception as e:
        return create_error_response(f"Internal server error: {str(e)}", 500)
