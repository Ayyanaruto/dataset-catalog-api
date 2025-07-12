from flask import Blueprint, request
from pydantic import ValidationError
from services.quality_log_service import QualityLogService
from models.quality_log import QualityLogCreate
from utils.helpers import serialize_doc, validate_object_id, create_error_response, create_success_response

quality_logs_bp = Blueprint('quality_logs', __name__)

def get_quality_log_service():
    return QualityLogService()

@quality_logs_bp.route('/datasets/<dataset_id>/quality-logs', methods=['POST'])
def create_quality_log(dataset_id):
    """
    Add a quality log for a dataset
    ---
    tags:
      - Quality Logs
    parameters:
      - in: path
        name: dataset_id
        type: string
        required: true
        description: Dataset ID
      - in: body
        name: quality_log
        description: Quality log data
        required: true
        schema:
          type: object
          required:
            - status
          properties:
            status:
              type: string
              enum: ["PASS", "FAIL"]
              example: "PASS"
            details:
              type: string
              example: "All data quality checks passed"
    responses:
      201:
        description: Quality log created successfully
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
        
        log_data = QualityLogCreate(**data)
        result = get_quality_log_service().create_quality_log(dataset_id, log_data)
        
        return create_success_response(
            serialize_doc(result),
            "Quality log created successfully",
            201
        )
        
    except ValidationError as e:
        return create_error_response(f"Validation error: {e}")
    except ValueError as e:
        return create_error_response(str(e), 404)
    except Exception as e:
        return create_error_response(f"Internal server error: {str(e)}", 500)

@quality_logs_bp.route('/datasets/<dataset_id>/quality-logs', methods=['GET'])
def get_quality_logs(dataset_id):
    """
    Get quality logs for a dataset
    ---
    tags:
      - Quality Logs
    parameters:
      - in: path
        name: dataset_id
        type: string
        required: true
        description: Dataset ID
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
        description: List of quality logs
      400:
        description: Invalid dataset ID
    """
    try:
        if not validate_object_id(dataset_id):
            return create_error_response("Invalid dataset ID")
        
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 20
        
        result = get_quality_log_service().get_quality_logs(dataset_id, page, limit)
        result['logs'] = serialize_doc(result['logs'])
        
        return create_success_response(result)
        
    except ValueError as e:
        return create_error_response(f"Invalid parameter: {e}")
    except Exception as e:
        return create_error_response(f"Internal server error: {str(e)}", 500)

@quality_logs_bp.route('/datasets/<dataset_id>/quality-summary', methods=['GET'])
def get_quality_summary(dataset_id):
    """
    Get quality summary for a dataset
    ---
    tags:
      - Quality Logs
    parameters:
      - in: path
        name: dataset_id
        type: string
        required: true
        description: Dataset ID
    responses:
      200:
        description: Quality summary
      400:
        description: Invalid dataset ID
    """
    try:
        if not validate_object_id(dataset_id):
            return create_error_response("Invalid dataset ID")
        
        summary = get_quality_log_service().get_quality_summary(dataset_id)
        return create_success_response(summary)
        
    except ValueError as e:
        return create_error_response(str(e))
    except Exception as e:
        return create_error_response(f"Internal server error: {str(e)}", 500)

@quality_logs_bp.route('/datasets/<dataset_id>/quality-status', methods=['GET'])
def get_latest_quality_status(dataset_id):
    """
    Get latest quality status for a dataset
    ---
    tags:
      - Quality Logs
    parameters:
      - in: path
        name: dataset_id
        type: string
        required: true
        description: Dataset ID
    responses:
      200:
        description: Latest quality status
      404:
        description: No quality logs found
    """
    try:
        if not validate_object_id(dataset_id):
            return create_error_response("Invalid dataset ID")
        
        status = get_quality_log_service().get_latest_quality_status(dataset_id)
        if not status:
            return create_error_response("No quality logs found for this dataset", 404)
        
        return create_success_response(serialize_doc(status))
        
    except Exception as e:
        return create_error_response(f"Internal server error: {str(e)}", 500)
