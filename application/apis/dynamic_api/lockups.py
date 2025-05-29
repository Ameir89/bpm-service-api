import json
import logging

from application.common.auth_middleware import token_required
from . import dynamic_api_blueprint
from application.common.general import General
from flask import request, jsonify, abort
from ...models.dynamic.lockups import Lockups


@dynamic_api_blueprint.route('/api/dynamic/lockups/create', methods=['POST'])
@token_required
def create_lockup(current_user):
    try:
        # Parse and validate request
        req = request.get_json(force=True)
        req_validation = General.request_validation(json_data=req, keys=[
            ["name", "required", None],
            ["status", None, None],
        ])

        if req_validation is not None:
            return jsonify({
                'message': 'Request parameter error',
                'data': req_validation,
                'success': False
            }), 400

        # Extract data from request

        name = req['name']
        display_name = req['display_name']
        status = req.get('status', 1)  # Optional


        # Process lockup creation
        result = Lockups.create_form_with_fields(name,display_name,status)

        # Check for errors in result
        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to create form',
                'error': result['error'],
                'success': False
            }), 500

        return jsonify({
            'message': 'Lockup created successfully',
            'data': result,
            'success': True
        }), 200

    except Exception as e:
        return jsonify({
            "error": "An internal server error occurred",
            "message": str(e),
            "data": None,
            "success": False
        }), 500

@dynamic_api_blueprint.route('/api/dynamic/lockups/<int:page>&<int:page_size>', methods=['GET'])
@token_required
def fetch_lockups(current_user,page,page_size):
    try:
         # Validate that page and page_size are integers and positive
        if not isinstance(page, int) or page < 1:
            return jsonify({
                'message': 'Invalid page parameter. Page must be a positive integer.',
                'success': False
            }), 400

        if not isinstance(page_size, int) or page_size < 1 or page_size > 100:
            return jsonify({
                'message': 'Invalid page_size parameter. Page size must be a positive integer between 1 and 100.',
                'success': False
            }), 400
            
        # Fetch data from the database
        result = Lockups.get_lockups(page,page_size)
        
        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to retrieve list of lockups',
                'error': result['error'],
                'success': False
            }), 500

        return jsonify({
            'message': 'Successfully retrieved list of lockups',
            'data': result['data'],  # Pass the lockups data
            'pagination': result['pagination'],  # Include pagination metadata
            'success': True
        }), 200

    except Exception as e:
        return jsonify({
            "error": "An internal server error occurred",
            "message": str(e),
            "data": None,
            "success": False
        }), 500
        
@dynamic_api_blueprint.route('/api/dynamic/lockups/<string:search_value>', methods=['GET'])
@token_required
def search_lockup(current_user,search_value):
    try:
        
        # Fetch data from the database
        result = Lockups.search_lockup_table(search_value)
        
        # Return the result
        return jsonify({
            'message': 'Data fetched successfully',
            'data': result,
            'success': True
        }), 200

    except Exception as e:
        General.write_event(f"Error in fetch_form_data: {str(e)}")
        logging.error(f"Error in fetch_form_data: {str(e)}")
        return jsonify({
            "error": "An internal server error occurred",
            "message": str(e),
            "data": None,
            "success": False
        }), 500


@dynamic_api_blueprint.route('/api/dynamic/lockups/<int:id>', methods=['GET'])
@token_required
def get_lockup(current_user,id):
    try:
        # Fetch data from the database
        result = Lockups.get_lockup_info(id)
        
        # Return the result
        return jsonify({
            'message': 'Data fetched successfully',
            'data': result,
            'success': True
        }), 200

    except Exception as e:
        General.write_event(f"Error in fetch_form_data: {str(e)}")
        logging.error(f"Error in fetch_form_data: {str(e)}")
        return jsonify({
            "error": "An internal server error occurred",
            "message": str(e),
            "data": None,
            "success": False
        }), 500


@dynamic_api_blueprint.route('/api/dynamic/lockups/<int:id>', methods=['PUT'])
@token_required
def update_lockup(current_user,id):
    try:
         # Parse and validate request
        req = request.get_json(force=True)
        req_validation = General.request_validation(json_data=req, keys=[
            ["display_name", "required", None],
            ["status", None, None],
        ])

        if req_validation is not None:
            return jsonify({
                'message': 'Request parameter error',
                'data': req_validation,
                'success': False
            }), 400

        # Extract data from request
        display_name = req['display_name']
        status = req.get('status', 1)  # Optional
        # Fetch data from the database
        result = Lockups.update_lockup(id,display_name , status)
        
        # Return the result
        return jsonify({
            'message': 'Updated data successfully' ,
            'data': result,
            'success': True if result else False
        }), 200

    except Exception as e:
        General.write_event(f"Error in update lockup data: {str(e)}")
        logging.error(f"Error in update lockup data: {str(e)}")
        return jsonify({
            "error": "An internal server error occurred",
            "message": str(e),
            "data": None,
            "success": False
        }), 500

@dynamic_api_blueprint.route('/api/dynamic/lockups/<int:id>', methods=['DELETE'])
@token_required
def delete_lockup(current_user,id):
    try:
        # Fetch data from the database
        result = Lockups.delete_lockup(id)
        
        # Return the result
        return jsonify({
            'message': 'Deleted data successfully' ,
            'data': result,
            'success': True if result else False
        }), 200

    except Exception as e:
        General.write_event(f"Error in delete lockup : {str(e)}")
        logging.error(f"Error in delete lockup : {str(e)}")
        return jsonify({
            "error": "An internal server error occurred",
            "message": str(e),
            "data": None,
            "success": False
        }), 500

@dynamic_api_blueprint.route('/api/dynamic/lockups/data', methods=['POST'])
@token_required
def add_lockup_data(current_user):
    try:
        # Parse and validate request
        req = request.get_json(force=True)
        req_validation = General.request_validation(json_data=req, keys=[
            ["lockup_id", "required", None],
            ["form_data", "required", None],
        ])
        
        if req_validation is not None:
            return jsonify({
                'message': 'Request parameter error',
                'data': req_validation,
                'success': False
            }), 400

        # Extract data from request
        lockup_id = req['lockup_id']
        form_data = req['form_data']
       
  
        # Process form data creation (Ensure any object from data is correctly formatted as JSON)
        for key, value in form_data.items():
            if isinstance(value, (dict, list)):  # Check if value is a dictionary or list
                form_data[key] = json.dumps(value)  # Convert to JSON string

        result = Lockups.create_lockup_data(lockup_id,form_data)

        # Check for errors in result
        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to create form',
                'error': result['error'],
                'success': False
            }), 500

        return jsonify({
            'message': 'Form created successfully',
            'data': result,
            'success': True
        }), 200

    except Exception as e:
        return jsonify({
            "error": "An internal server error occurred",
            "message": str(e),
            "data": None,
            "success": False
        }), 500


@dynamic_api_blueprint.route('/api/dynamic/lockups/data/<int:lockup_id>/<int:page>&<int:page_size>', methods=['GET'])
@token_required
def fetch_lockup_data(current_user,lockup_id,page,page_size):
    try:
        # Validate that page and page_size are integers and positive
        if not isinstance(page, int) or page < 1:
            return jsonify({
                'message': 'Invalid page parameter. Page must be a positive integer.',
                'success': False
            }), 400

        if not isinstance(page_size, int) or page_size < 1 or page_size > 100:
            return jsonify({
                'message': 'Invalid page_size parameter. Page size must be a positive integer between 1 and 100.',
                'success': False
            }), 400
        # Fetch data from the database
        result = Lockups.get_lockup_table_data(lockup_id,page,page_size)
        
        # Return the result
        return jsonify({
            'message': 'Data fetched successfully',
            'data': result,
            'success': True
        }), 200

    except Exception as e:
        General.write_event(f"Error in fetch_form_data: {str(e)}")
        logging.error(f"Error in fetch_form_data: {str(e)}")
        return jsonify({
            "error": "An internal server error occurred",
            "message": str(e),
            "data": None,
            "success": False
        }), 500

@dynamic_api_blueprint.route('/api/dynamic/lockups/data/<int:lockup_id>/<string:search_value>', methods=['GET'])
@token_required
def search_lockup_data(current_user,lockup_id,search_value):
    try:
        
        # Fetch data from the database
        result = Lockups.search_lockup_table_data(lockup_id,search_value)
        
        # Return the result
        return jsonify({
            'message': 'Data fetched successfully',
            'data': result,
            'success': True
        }), 200

    except Exception as e:
        General.write_event(f"Error in fetch_form_data: {str(e)}")
        logging.error(f"Error in fetch_form_data: {str(e)}")
        return jsonify({
            "error": "An internal server error occurred",
            "message": str(e),
            "data": None,
            "success": False
        }), 500

@dynamic_api_blueprint.route('/api/dynamic/lockups/<int:lockup_id>/data/<int:insert_id>', methods=['DELETE'])
@token_required
def delete_lockup_data(current_user,lockup_id,insert_id):  
    try:
        result = Lockups.delete_lockup_data(lockup_id,insert_id)

        # Check for errors in result
        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to deleted data',
                'error': result['error'],
                'success': False
            }), 500

        return jsonify({
            'message': 'Deleted record  successfully',
            'data': result,
            'success': True
        }), 200

    except Exception as e:
        return jsonify({
            "error": "An internal server error occurred",
            "message": str(e),
            "data": None,
            "success": False
        }), 500     

@dynamic_api_blueprint.route('/api/dynamic/lockups/<int:lockup_id>/data/<int:insert_id>', methods=['PUT'])
@token_required
def update_lockup_data(current_user,lockup_id,insert_id):
    try:
         # Parse and validate request
        req = request.get_json(force=True)
        req_validation = General.request_validation(json_data=req, keys=[
            ["name", "required", None],
        ])

        if req_validation is not None:
            return jsonify({
                'message': 'Request parameter error',
                'data': req_validation,
                'success': False
            }), 400

        # Extract data from request
        name = req['name']
        # Fetch data from the database
        result = Lockups.update_lockup_data(lockup_id=lockup_id,id=insert_id,name=name)
        if result["success"] == False:
            return jsonify({
                'message': 'Cannot Update data' ,
                'data': result["error"],
                'success': False 
            }), 400
        # Return the result
        return jsonify({
            'message': 'Updated data successfully' ,
            'data': result,
            'success': True
        }), 200

    except Exception as e:
        General.write_event(f"Error in update lockup data: {str(e)}")
        logging.error(f"Error in update lockup data: {str(e)}")
        return jsonify({
            "error": "An internal server error occurred",
            "message": str(e),
            "data": None,
            "success": False
        }), 500
        
@dynamic_api_blueprint.errorhandler(403)
def forbidden(e):
    return jsonify({
        "message": "Forbidden",
        "error": str(e),
        "data": None,
        "success": False
    }), 403


@dynamic_api_blueprint.errorhandler(404)
def not_found(e):
    return jsonify({
        "message": "Endpoint Not Found",
        "error": str(e),
        "data": None,
        "success": False
    }), 404


@dynamic_api_blueprint.errorhandler(500)
def internal_server_error(e):
    return jsonify({
        "message": "Internal Server Error",
        "error": str(e),
        "data": None,
        "success": False
    }), 500
