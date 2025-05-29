from application.common.auth_middleware import token_required
from . import lockups_api_blueprint
from application.common.general import General
from flask import request, jsonify, abort
from ...models.lockups.levels import Levels

"""create group API."""
@lockups_api_blueprint.route('/api/lockups/levels/add', methods=['POST'])
@token_required
def create_group_level(current_user):
    try:
        req = request.get_json(force=True)
        req_validation = General.request_validation(json_data=req, keys=[
            ["name", "required", None],
            ["ar_name", None, None],
        ])

        if req_validation is not None:
            return jsonify({
                'message': 'Request parameter error',
                'data': req_validation,
                'success': False
            }), 400

        name = req['name']
        ar_name = req['ar_name']
       

        level = Levels()
        result = level.create_level(name, ar_name)

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
@lockups_api_blueprint.route('/api/lockups/levels/<int:level_id>', methods=['PUT'])
@token_required
def update_level(current_user,level_id):
    try:
        req = request.get_json(force=True)
        req_validation = General.request_validation(json_data=req, keys=[
            ["name", "required", None],
            ["ar_name", None, None],
        ])

        if req_validation is not None:
            return jsonify({
                'message': 'Request parameter error',
                'data': req_validation,
                'success': False
            }), 400

        name = req['name']
        ar_name = req['ar_name']
        level = Levels()
        result = level.update_group_level_data(level_id,name,ar_name)

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to update group level',
                'error': result['error'],
                'success': False
            }), 500

        return jsonify({
            'message': 'Group level updated successfully',
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

"""get group level by id API."""
@lockups_api_blueprint.route('/api/lockups/levels/<int:level_id>', methods=['GET'])
@token_required
def get_level(current_user,level_id):
    try:
        level = Levels()
        result = level.get_level(level_id)

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to retrieve group level info',
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

"""delete group level by id API."""
@lockups_api_blueprint.route('/api/lockups/levels/<int:level_id>', methods=['DELETE'])
@token_required
def delete_group_level(current_user,level_id):
    try:
        level = Levels()
        result = level.delete_group_level(level_id)

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to delete group level',
                'error': result['error'],
                'success': False
            }), 400

        return jsonify({
            'message': 'Group level deleted successfully',
            'data': {'level_id': level_id},
            'success': True
        }), 200

    except ValueError as ve:
        return jsonify({
            "error": "Invalid input provided",
            "message": str(ve),
            "data": None,
            "success": False
        }), 400

    except Exception as e:
        return jsonify({
            "error": "An internal server error occurred",
            "message": str(e),
            "data": None,
            "success": False
        }), 500

"""return list of group levels API."""
@lockups_api_blueprint.route('/api/lockups/levels', methods=['GET'])
@token_required
def list_groups(current_user):
    try:

        # Call Group Level service to fetch paginated data
        level = Levels()
        result = level.list_group_levels()
        
        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to retrieve list of group level',
                'error': result,
                'success': False
            }), 500

        return jsonify({
            'message': 'Successfully retrieved list of groups',
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
