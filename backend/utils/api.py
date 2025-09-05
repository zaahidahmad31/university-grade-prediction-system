from flask import jsonify

def api_response(data=None, message=None, status=200, meta=None):
    """Create a standardized API response"""
    response = {
        'status': 'success' if status < 400 else 'error',
    }
    
    if message:
        response['message'] = message
    
    if data is not None:
        response['data'] = data
    
    if meta:
        response['meta'] = meta
        
    return jsonify(response), status

def error_response(message, status=400, errors=None):
    """Create a standardized error response"""
    response = {
        'status': 'error',
        'message': message
    }
    
    if errors:
        response['errors'] = errors
        
    return jsonify(response), status

def paginated_response(items, page, per_page, total):
    """Create a paginated response"""
    return api_response(
        data=items,
        meta={
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }
    )