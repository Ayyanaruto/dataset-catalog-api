from bson import ObjectId
from datetime import datetime
from flask import jsonify

def serialize_doc(doc):
    """Convert MongoDB document to JSON serializable format"""
    if doc is None:
        return None
    
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    
    if isinstance(doc, dict):
        serialized = {}
        for key, value in doc.items():
            if key == '_id':
                serialized['id'] = str(value)
            elif isinstance(value, ObjectId):
                serialized[key] = str(value)
            elif isinstance(value, datetime):
                serialized[key] = value.isoformat()
            elif isinstance(value, dict):
                serialized[key] = serialize_doc(value)
            elif isinstance(value, list):
                serialized[key] = serialize_doc(value)
            else:
                serialized[key] = value
        return serialized
    
    return doc

def validate_object_id(id_string):
    """Validate if string is a valid ObjectId"""
    try:
        ObjectId(id_string)
        return True
    except:
        return False

def create_error_response(message, status_code=400):
    """Create standardized error response"""
    return jsonify({"error": message}), status_code

def create_success_response(data, message=None, status_code=200):
    """Create standardized success response"""
    response = {"data": data}
    if message:
        response["message"] = message
    return jsonify(response), status_code
