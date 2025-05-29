from application.common.auth_middleware import token_required
from . import workflow_api_blueprint
from application.common.general import General
from flask import request, jsonify, abort
from ...models.workflow.workflow import Workflows

"""create workflow API."""
@workflow_api_blueprint.route('/api/workflows', methods=['POST'])
@token_required
def create_workflow(current_user):
    try:
        req = request.get_json(force=True)
        req_validation = General.request_validation(json_data=req, keys=[
            ["label", "required", None],
            ["name", "required", None],
            ["description", None, None],
            ["status", None, None],
        ])

        if req_validation is not None:
            return jsonify({
                'message': 'Request parameter error',
                'data': req_validation,
                'success': False
            }), 400
        
        label = req['label']
        name = req['name']
        description = req['description']
        status = req.get('status', 0)  # Default status to 0 if not provided
        created_by = current_user.get("id") # Placeholder for session user ID

        workflow = Workflows()
        result = workflow.create_workflow(label, name, description, status, created_by)

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to create workflow',
                'error': result['error'],
                'success': False
            }), 500

        return jsonify({
            'message': 'workflow created successfully',
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


"""update workflow API."""
@workflow_api_blueprint.route('/api/workflows/<int:workflow_id>', methods=['PUT'])
@token_required
def update_workflow(current_user, workflow_id):
    try:
        req = request.get_json(force=True)
        req_validation = General.request_validation(json_data=req, keys=[
            ["label", "required", None],
            ["name", "required", None],
            ["description", "required", None],
            ["status", None, None],
        ])

        if req_validation is not None:
            return jsonify({
                'message': 'Request parameter error',
                'data': req_validation,
                'success': False
            }), 400

        label = req['label']
        name = req['name']
        description = req['description']
        status = req['status']
        
        workflow = Workflows()
        result = workflow.update_workflow_data(label, name,description, status,workflow_id)

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

"""get workflow by id API."""
@workflow_api_blueprint.route('/api/workflows/<int:workflow_id>', methods=['GET'])
@token_required
def get_workflow(current_user,workflow_id):
    try:
        workflow = Workflows()
        result = workflow.get_workflow(workflow_id)

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to retrieve group info',
                'error': result['error'],
                'success': False
            }), 404

        return jsonify({
            'message': 'Successfully retrieved group info',
            'data': result["data"],
            'success': True
        }), 200

    except Exception as e:
        return jsonify({
            "error": "An internal server error occurred",
            "message": str(e),
            "data": None,
            "success": False
        }), 500


      
"""change status workflow by id API."""
@workflow_api_blueprint.route('/api/workflows/changestatus/<int:workflow_id>', methods=['PUT'])
@token_required
def change_workflow_status(current_user,workflow_id):
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

        workflow = Workflows()
        result = workflow.workflow(workflow_id, status)

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to change workflow status',
                'error': result['error'],
                'success': False
            }), 500

        return jsonify({
            'message': 'Workflow status changed successfully',
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

"""delete workflow by id API."""
@workflow_api_blueprint.route('/api/workflows/<int:workflow_id>', methods=['DELETE'])
@token_required
def delete_workflow(current_user,workflow_id):
    try:
        workflow = Workflows()
        result = workflow.delete_workflow(workflow_id)

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to delete workflow',
                'error': result['error'],
                'success': False
            }), 400

        return jsonify({
            'message': 'Workflow deleted successfully',
            'data': {'workflow_id': workflow_id},
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

"""return list of workflows API."""
@workflow_api_blueprint.route('/api/workflows/<int:page>&<int:page_size>', methods=['GET'])
@token_required
def list_workflows(current_user,page,page_size):
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
        workflow = Workflows()
        result = workflow.list_workflows(page, page_size)
        # print(result)
        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to retrieve list of workflows',
                'error': result['error'],
                'success': False
            }), 500

        return jsonify({
            'message': 'Successfully retrieved list of workflows',
            'data': result['data'],  # Pass the workflows data
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


# """assign group to activity API."""
# @workflow_api_blueprint.route('/api/activities/<int:activity_id>/assign-group', methods=['POST'])
# @token_required
# def assign_group_to_activity(current_user,activity_id):
#     try:
#         req = request.get_json(force=True)
#         req_validation = General.request_validation(json_data=req, keys=[
#             ["group_id", "required", None],
#         ])

#         if req_validation is not None:
#             return jsonify({
#                 'message': 'Request parameter error',
#                 'data': req_validation,
#                 'success': False
#             }), 400

#         group_id = req['group_id']

#         group = Groups()
#         result = group.assign_group_to_activity(activity_id, group_id)

#         if isinstance(result, dict) and 'error' in result:
#             return jsonify({
#                 'message': 'Failed to assign group to activity',
#                 'error': result['error'],
#                 'success': False
#             }), 500

#         return jsonify({
#             'message': 'Group assigned to activity successfully',
#             'data': result,
#             'success': True
#         }), 200

#     except Exception as e:
#         return jsonify({
#             "error": "An internal server error occurred",
#             "message": str(e),
#             "data": None,
#             "success": False
#         }), 500

@workflow_api_blueprint.errorhandler(403)
def forbidden(e):
    return jsonify({
        "message": "Forbidden",
        "error": str(e),
        "data": None,
        "success": False
    }), 403
    
@workflow_api_blueprint.errorhandler(404)
def not_found(e):
    return jsonify({
        "message": "Endpoint Not Found",
        "error": str(e),
        "data": None,
        "success": False
    }), 404

@workflow_api_blueprint.errorhandler(500)
def internal_server_error(e):
    return jsonify({
        "message": "Internal Server Error",
        "error": str(e),
        "data": None,
        "success": False
    }), 500
