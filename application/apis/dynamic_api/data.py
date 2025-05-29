import json
import logging

from application.common.auth_middleware import token_required
from . import dynamic_api_blueprint
from application.common.general import General
from flask import request, jsonify, abort
from ...models.dynamic.data import Data


@dynamic_api_blueprint.route('/api/dynamic/data/addData', methods=['POST'])
# @token_required
def add_form_data():
    try:
        # Parse and validate request
        req = request.get_json(force=True)
        req_validation = General.request_validation(json_data=req, keys=[
            ["table_name", "required", None],
            ["form_data", "required", None],
        ])
        
        if req_validation is not None:
            return jsonify({
                'message': 'Request parameter error',
                'data': req_validation,
                'success': False
            }), 400

        # Extract data from request
        table_name = req['table_name']
        form_data = req['form_data']
        
        # Validate table name is exist
        # if not General.validate_table_name(table_name):
        #     return jsonify({
        #         'message': 'Invalid table name format',
        #         'success': False
        #     }), 400
        
        # Process form data creation (Ensure any object from data is correctly formatted as JSON)
        for key, value in form_data.items():
            if isinstance(value, (dict, list)):  # Check if value is a dictionary or list
                form_data[key] = json.dumps(value)  # Convert to JSON string

        result = Data.create_form_data(table_name,form_data)

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


@dynamic_api_blueprint.route('/api/dynamic/data/fetchData', methods=['POST'])
# @token_required
def fetch_form_data():
    try:
        # Parse and validate request
        req = request.get_json(force=True)
        req_validation = General.request_validation(json_data=req, keys=[
            ["table_name", "required", None],
            ["columns", None, None],
            ["limit", None, None],
            ["offset", None, None],
        ])
        
        if req_validation is not None:
            return jsonify({
                'message': 'Request parameter error',
                'data': req_validation,
                'success': False
            }), 400

        # Extract parameters from the request
        table_name = req.get("table_name")
        columns = req.get("columns", None)
        limit = req.get("limit", None)
        offset = req.get("offset", None)
        
        print(table_name)
        # Validate table name and ensure it's safe to use
        allowed_tables = ["form_customer_feedback", "another_table_name"]  # Add valid table names here
        if table_name not in allowed_tables:
            return jsonify({
                'message': 'Invalid table name',
                'success': False
            }), 400
         
        # Handle columns parameter
        if columns:
            if not isinstance(columns, list):
                return jsonify({
                    'message': 'Columns must be a list',
                    'success': False
                }), 400
            columns = [f"`{col}`" for col in columns]  # Sanitize column names (to prevent SQL injection)
            columns = ", ".join(columns)
        else:
            columns = "*"  # Select all columns by default

        # Handle pagination (limit and offset)
        if limit is not None:
            try:
                limit = int(limit)
                if limit < 1:
                    raise ValueError("Limit must be a positive integer.")
            except ValueError:
                return jsonify({
                    'message': 'Limit must be a positive integer',
                    'success': False
                }), 400
        if offset is not None:
            try:
                offset = int(offset)
                if offset < 0:
                    raise ValueError("Offset cannot be negative.")
            except ValueError:
                return jsonify({
                    'message': 'Offset must be a non-negative integer',
                    'success': False
                }), 400

        # Fetch data from the database
        result = Data.fetch_form_data(table_name=table_name, columns=columns, limit=limit, offset=offset)
        
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
