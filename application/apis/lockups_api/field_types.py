from application.common.auth_middleware import token_required
from . import lockups_api_blueprint
from application.common.general import General
from flask import request, jsonify
from ...models.lockups.filed_types import FieldTypes

"""create field type API."""
@lockups_api_blueprint.route('/api/lockups/field_types', methods=['POST'])
@token_required
def create_field_type(current_user):
    try:
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

        name = req['name']
        instance = FieldTypes()
        result = instance.create_field_type(name)
        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to create field type',
                'error': result['error'],
                'success': False
            }), 500

        return jsonify({
            'message': 'field type created successfully',
            'data': result,
            'success': True
        }), 201

    except Exception as e:
        return jsonify({
            "error": "An internal server error occurred",
            "message": str(e),
            "data": None,
            "success": False
        }), 500


"""update field type API."""
@lockups_api_blueprint.route('/api/lockups/field_types/<int:field_type_id>', methods=['PUT'])
@token_required
def update_field_types(current_user, field_type_id):
    try:
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

        name = req['name']
        instance = FieldTypes()
        result = instance.update_field_type(field_type_id, name)

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to update action type',
                'error': result['error'],
                'success': False
            }), 500

        return jsonify({
            'message': 'action type updated successfully',
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


"""get field type by id API."""
@lockups_api_blueprint.route('/api/lockups/field_types/<int:field_type_id>', methods=['GET'])
@token_required
def get_field_type(current_user, field_type_id):
    try:
        instance = FieldTypes()
        result = instance.get_field_type(field_type_id)

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to retrieve action type info',
                'error': result['error'],
                'success': False
            }), 404

        return jsonify({
            'message': 'Successfully retrieved group level info',
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


"""return list of field levels API."""
@lockups_api_blueprint.route('/api/lockups/field_types', methods=['GET'])
@token_required
def list_field_types(current_user):
    try:
        # Call field service to fetch paginated data
        instance = FieldTypes()
        result = instance.list_field_types()

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to retrieve list of action types list',
                'error': result,
                'success': False
            }), 500

        return jsonify({
            'message': 'Successfully retrieved list of field type',
            'data': result,  # Pass the groups data
            'success': True
        }), 200

    except Exception as e:
        return jsonify({
            "error": "An internal server error occurred",
            "message": str(e),
            "data": None,
            "success": False
        }), 500




@lockups_api_blueprint.errorhandler(403)
def forbidden(e):
    return jsonify({
        "message": "Forbidden",
        "error": str(e),
        "data": None,
        "success": False
    }), 403


@lockups_api_blueprint.errorhandler(404)
def not_found(e):
    return jsonify({
        "message": "Endpoint Not Found",
        "error": str(e),
        "data": None,
        "success": False
    }), 404


@lockups_api_blueprint.errorhandler(500)
def internal_server_error(e):
    return jsonify({
        "message": "Internal Server Error",
        "error": str(e),
        "data": None,
        "success": False
    }), 500
