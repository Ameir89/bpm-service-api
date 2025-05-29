from application.common.auth_middleware import token_required
from . import workflow_api_blueprint
from application.common.general import General
from flask import request, jsonify, abort
from ...models.workflow.tasks import Tasks

"""create task API."""
@workflow_api_blueprint.route('/api/workflows/tasks', methods=['POST'])
@token_required
def create_task(current_user):
    try:
        req = request.get_json(force=True)
        req_validation = General.request_validation(json_data=req, keys=[
            ["workflow_id", "required", None],
            ["name", "required", None],
            ["task_type", None, None],
        ])

        if req_validation is not None:
            return jsonify({
                'message': 'Request parameter error',
                'data': req_validation,
                'success': False
            }), 400
        
        workflow_id = req['workflow_id']
        name = req['name']
        task_type = req.get('task_type', 'manual')
        task = Tasks()
        result = task.create_task(workflow_id, name, task_type)

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to create task',
                'error': result['error'],
                'success': False
            }), 500

        return jsonify({
            'message': 'task created successfully',
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


"""update task API."""
@workflow_api_blueprint.route('/api/workflows/tasks/<int:task_id>', methods=['PUT'])
@token_required
def update_task(current_user, task_id):
    try:
        req = request.get_json(force=True)
        req_validation = General.request_validation(json_data=req, keys=[
            ["workflow_id", "required", None],
            ["name", "required", None],
            ["task_type", None, None],
        ])

        if req_validation is not None:
            return jsonify({
                'message': 'Request parameter error',
                'data': req_validation,
                'success': False
            }), 400

        workflow_id = req['workflow_id']
        name = req['name']
        task_type = req['task_type']
        
        task = Tasks()
        result = task.update_task(task_id, workflow_id, name, task_type)

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to update task',
                'error': result['error'],
                'success': False
            }), 500

        return jsonify({
            'message': 'Task updated successfully',
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


"""get all tasks for template API."""
@workflow_api_blueprint.route('/api/workflows/tasks/<int:workflow_id>', methods=['GET'])
@token_required
def get_all_tasks(current_user, workflow_id):
    try:
        task = Tasks()
        result = task.get_all_tasks(workflow_id)

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to retrieve all tasks',
                'error': result['error'],
                'success': False
            }), 404

        return jsonify({
            'message': 'Successfully retrieved all tasks',
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


"""get task by id API."""
@workflow_api_blueprint.route('/api/workflows/task/<int:task_id>', methods=['GET'])
@token_required
def get_task(current_user, task_id):
    try:
        task = Tasks()
        result = task.get_task(task_id)

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to retrieve task info',
                'error': result['error'],
                'success': False
            }), 404

        return jsonify({
            'message': 'Successfully retrieved task info',
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


"""delete task by id API."""
@workflow_api_blueprint.route('/api/workflows/tasks/<int:task_id>', methods=['DELETE'])
@token_required
def delete_task(current_user, task_id):
    try:
        task = Tasks()
        result = task.delete_task(task_id)

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to delete task',
                'error': result['error'],
                'success': False
            }), 400

        return jsonify({
            'message': 'Task deleted successfully',
            'data': {'task_id': task_id},
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


# """assign task to group API."""
# @workflow_api_blueprint.route('/api/workflows/tasks/assign_group', methods=['POST'])
# @token_required
# def assign_task_to_group(current_user):
#     try:
#         req = request.get_json(force=True)
#         req_validation = General.request_validation(json_data=req, keys=[
#             ["task_id", "required", None],
#             ["group_id", "required", None],
#         ])
#
#         if req_validation is not None:
#             return jsonify({
#                 'message': 'Request parameter error',
#                 'data': req_validation,
#                 'success': False
#             }), 400
#
#         task_id = req['task_id']
#         group_id = req['group_id']
#
#         task = Tasks()
#         result = task.assign_task_group(task_id, group_id)
#
#         if isinstance(result, dict) and 'error' in result:
#             return jsonify({
#                 'message': 'Failed to assign task to group',
#                 'error': result['error'],
#                 'success': False
#             }), 500
#
#         return jsonify({
#             'message': 'assign task to group successfully',
#             'data': result,
#             'success': True
#         }), 200
#
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
