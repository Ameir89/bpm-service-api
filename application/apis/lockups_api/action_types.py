from application.common.auth_middleware import token_required
from . import lockups_api_blueprint
from application.common.general import General
from flask import request, jsonify, abort
from ...models.lockups.action_types import ActionTypes

"""create action type API."""
@lockups_api_blueprint.route('/api/lockups/action_types', methods=['POST'])
@token_required
def create_action_type(current_user):
    try:
        req = request.get_json(force=True)
        req_validation = General.request_validation(json_data=req, keys=[
            ["name", "required", None],
            ["color", None, None],
        ])

        if req_validation is not None:
            return jsonify({
                'message': 'Request parameter error',
                'data': req_validation,
                'success': False
            }), 400

        name = req['name']
        color = req['color']
        instance = ActionTypes()
        result = instance.create_action_type(name, color)
        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to create group',
                'error': result['error'],
                'success': False
            }), 500

        return jsonify({
            'message': 'Group Level created successfully',
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


"""update group level API."""
@lockups_api_blueprint.route('/api/lockups/action_types/<int:action_type_id>', methods=['PUT'])
@token_required
def update_action_types(current_user, action_type_id):
    try:
        req = request.get_json(force=True)
        req_validation = General.request_validation(json_data=req, keys=[
            ["name", "required", None],
            ["color", None, None],
        ])

        if req_validation is not None:
            return jsonify({
                'message': 'Request parameter error',
                'data': req_validation,
                'success': False
            }), 400

        name = req['name']
        color = req['color']
        instance = ActionTypes()
        result = instance.update_action_type(action_type_id, name, color)

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


"""get action type by id API."""


@lockups_api_blueprint.route('/api/lockups/action_types/<int:action_type_id>', methods=['GET'])
@token_required
def get_action_type(current_user, action_type_id):
    try:
        instance = ActionTypes()
        result = instance.get_action_type(action_type_id)

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


"""return list of group levels API."""
@lockups_api_blueprint.route('/api/lockups/action_types', methods=['GET'])
@token_required
def list_action_types(current_user):
    try:
        # Call Group Level service to fetch paginated data
        instance = ActionTypes()
        result = instance.list_action_types()

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to retrieve list of action types list',
                'error': result,
                'success': False
            }), 500

        return jsonify({
            'message': 'Successfully retrieved list of action type',
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


"""return list of enums action types API."""
@lockups_api_blueprint.route('/api/lockups/action_types/enums', methods=['GET'])
@token_required
def list_action_types_enums(current_user):
    try:
        # Get action type enums
        instance = ActionTypes()
        result = instance.list_action_types_enums()

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to retrieve list of action types list',
                'error': result,
                'success': False
            }), 500

        return jsonify({
            'message': 'Successfully retrieved list of action type',
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
