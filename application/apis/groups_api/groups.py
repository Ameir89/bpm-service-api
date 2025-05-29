from application.common.auth_middleware import token_required
from . import groups_api_blueprint
from application.common.general import General
from flask import request, jsonify, abort
from ...models.groups.groups import Groups

"""create group API."""
@groups_api_blueprint.route('/api/groups/create', methods=['POST'])
@token_required
def create_group(current_user):
    try:
        req = request.get_json(force=True)
        req_validation = General.request_validation(json_data=req, keys=[
            ["group_name", "required", None],
            ["description", "required", None],
            ["status", None, None],
        ])

        if req_validation is not None:
            return jsonify({
                'message': 'Request parameter error',
                'data': req_validation,
                'success': False
            }), 400

        group_name = req['group_name']
        description = req['description']
        status = req.get('status', 0)  # Default status to 0 if not provided
        created_by = 1  # Placeholder for session user ID

        group = Groups()
        result = group.create_group(group_name, description, status, created_by)

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to create group',
                'error': result['error'],
                'success': False
            }), 500

        return jsonify({
            'message': 'Group created successfully',
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

"""update group API."""
@groups_api_blueprint.route('/api/groups/<int:group_id>', methods=['PUT'])
@token_required
def update_group(current_user,group_id):
    try:
        req = request.get_json(force=True)
        req_validation = General.request_validation(json_data=req, keys=[
            ["group_name", "required", None],
            ["description", "required", None],
            ["status", None, None],
        ])

        if req_validation is not None:
            return jsonify({
                'message': 'Request parameter error',
                'data': req_validation,
                'success': False
            }), 400

        group_name = req['group_name']
        description = req['description']
        status = req['status']
        group = Groups()
        result = group.update_group_data(group_id, group_name, description, status)

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to update group',
                'error': result['error'],
                'success': False
            }), 500

        return jsonify({
            'message': 'Group updated successfully',
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

"""get group by id API."""
@groups_api_blueprint.route('/api/groups/<int:group_id>', methods=['GET'])
@token_required
def get_group(current_user,group_id):
    try:
        group = Groups()
        result = group.get_group(group_id)

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to retrieve group info',
                'error': result['error'],
                'success': False
            }), 404

        return jsonify({
            'message': 'Successfully retrieved group info',
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
"""get group by name API."""
@groups_api_blueprint.route('/api/groups/<string:group_name>', methods=['GET'])
@token_required
def get_group_by_name(current_user,group_name):
    """
    API to retrieve group details by its name, with partial matching support.
    """
    try:
        # Validate the input
        if not group_name:
            return jsonify({
                'message': 'Group name is required.',
                'error': 'Invalid input: group_name is missing.',
                'success': False
            }), 400

        # Instantiate the Groups class and retrieve group details
        group = Groups()
        result = group.get_group_name(group_name)

        # Check if the group was found
        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to retrieve group info.',
                'error': result['error'],
                'success': False
            }), 404

        # Successfully retrieved the group
        return jsonify({
            'message': 'Successfully retrieved group info.',
            'data': result,
            'success': True
        }), 200

    except Exception as e:
        # Handle unexpected errors
        return jsonify({
            "message": "An internal server error occurred.",
            "error": str(e),
            "data": None,
            "success": False
        }), 500
        
"""change status group by id API."""
@groups_api_blueprint.route('/api/groups/changestatus/<int:group_id>', methods=['PUT'])
@token_required
def change_group_status(current_user,group_id):
    try:
        req = request.get_json(force=True)
        req_validation = General.request_validation(json_data=req, keys=[
            ["status", "required", None],
        ])

        if req_validation is not None:
            return jsonify({
                'message': 'Request parameter error',
                'data': req_validation,
                'success': False
            }), 400

        status = req['status']

        group = Groups()
        result = group.change_group_status(group_id, status)

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to change group status',
                'error': result['error'],
                'success': False
            }), 500

        return jsonify({
            'message': 'Group status changed successfully',
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

"""delete group by id API."""
@groups_api_blueprint.route('/api/groups/<int:group_id>', methods=['DELETE'])
@token_required
def delete_group_by_id(current_user,group_id):
    try:
        group = Groups()
        result = group.delete_group(group_id)

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to delete group',
                'error': result['error'],
                'success': False
            }), 400

        return jsonify({
            'message': 'Group deleted successfully',
            'data': {'group_id': group_id},
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

"""return list of groups API."""
@groups_api_blueprint.route('/api/groups/<int:page>&<int:page_size>', methods=['GET'])
@token_required
def list_groups(current_user,page,page_size):
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

        # Call Groups service to fetch paginated data
        group = Groups()
        result = group.list_groups(page, page_size)
        # print(result)
        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to retrieve list of groups',
                'error': result['error'],
                'success': False
            }), 500

        return jsonify({
            'message': 'Successfully retrieved list of groups',
            'data': result['data'],  # Pass the groups data
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


"""assign group to activity API."""
@groups_api_blueprint.route('/api/activities/<int:activity_id>/assign-group', methods=['POST'])
@token_required
def assign_group_to_activity(current_user,activity_id):
    try:
        req = request.get_json(force=True)
        req_validation = General.request_validation(json_data=req, keys=[
            ["group_id", "required", None],
        ])

        if req_validation is not None:
            return jsonify({
                'message': 'Request parameter error',
                'data': req_validation,
                'success': False
            }), 400

        group_id = req['group_id']

        group = Groups()
        result = group.assign_group_to_activity(activity_id, group_id)

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to assign group to activity',
                'error': result['error'],
                'success': False
            }), 500

        return jsonify({
            'message': 'Group assigned to activity successfully',
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

@groups_api_blueprint.errorhandler(403)
def forbidden(e):
    return jsonify({
        "message": "Forbidden",
        "error": str(e),
        "data": None,
        "success": False
    }), 403
    
@groups_api_blueprint.errorhandler(404)
def not_found(e):
    return jsonify({
        "message": "Endpoint Not Found",
        "error": str(e),
        "data": None,
        "success": False
    }), 404

@groups_api_blueprint.errorhandler(500)
def internal_server_error(e):
    return jsonify({
        "message": "Internal Server Error",
        "error": str(e),
        "data": None,
        "success": False
    }), 500
