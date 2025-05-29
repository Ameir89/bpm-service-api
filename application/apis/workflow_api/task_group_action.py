from application.common.auth_middleware import token_required
from . import workflow_api_blueprint
from application.common.general import General
from flask import request, jsonify, abort
from ...models.workflow.task_group_action import TasksGroupAction

"""create task group workflow API."""

@workflow_api_blueprint.route('/api/workflows/task_group_action/<int:task_id>', methods=['PUT'])
@token_required
def create_task_group_action(current_user, task_id):
    try:
        req = request.get_json(force=True)

        # Expecting a list of objects
        if not isinstance(req, list):
            return jsonify({
                'message': 'Invalid data format: expected a list of objects.',
                'success': False
            }), 400

        data = []
        for item in req:
            # Validate required fields
            if not all(k in item for k in ("group_id", "action", "level")):
                return jsonify({
                    'message': 'Missing required fields in some items.',
                    'success': False
                }), 400
            
            data.append({
                "task_id": task_id,
                "group_id": item["group_id"],
                "action": item["action"],
                "level": item["level"]
            })


        workflow = TasksGroupAction()
        
        try:
            result = workflow.create_task_group_action(data)
        except Exception as db_error:
            # Catch unexpected errors inside the function
            return jsonify({
                'message': 'Error while creating task group actions.',
                'error': str(db_error),
                'success': False
            }), 500

         # Expecting: {'inserted_ids': 2, 'success': True}
        if not (isinstance(result, dict) and result.get("success") is True):
            return jsonify({
                'message': 'Unexpected response from create_task_group_action',
                'error': str(result),
                'success': False
            }), 500

        # Format response output
        response_data = [
            {"group_id": item["group_id"], "action": item["action"], "level": item["level"]}
            for item in data
        ]

        return jsonify(response_data), 201

    except Exception as e:
        return jsonify({
            "error": "An internal server error occurred",
            "message": str(e),
            "success": False
        }), 500

"""update workflow API."""
@workflow_api_blueprint.route('/api/workflows/task_group_action/<int:record_id>', methods=['PUT'])
@token_required
def update_task_group_action(current_user, record_id):
    try:
        req = request.get_json(force=True)
        req_validation = General.request_validation(json_data=req, keys=[
            ["task_id", "required", None],
            ["group", "required", None],
            ["action", "required", None],
            ["level", "required", None],
        ])

        if req_validation is not None:
            return jsonify({
                'message': 'Request parameter error',
                'data': req_validation,
                'success': False
            }), 400

        task_id = req['task_id']
        group = req['group']
        action = req['action']
        level = req['level']

        workflow = TasksGroupAction()
        result = workflow.update_task_group_action(record_id, task_id, group, action, level)
        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to update task group action',
                'error': result['error'],
                'success': False
            }), 500

        return jsonify({
            'message': 'Task group action updated successfully',
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
@workflow_api_blueprint.route('/api/workflows/task_group_action/<int:task_id>', methods=['GET'])
@token_required
def get_task_group_action(current_user, task_id):
    try:
        workflow = TasksGroupAction()
        result = workflow.get_task_group_action(task_id)

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to retrieve task group action info',
                'error': result['error'],
                'success': False
            }), 404

        return jsonify({
            'message': 'Successfully retrieved task group action info',
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


"""delete TasksGroupWorkflow by id API."""
@workflow_api_blueprint.route('/api/workflows/task_group_action/<int:record_id>', methods=['DELETE'])
@token_required
def delete_task_group_action(current_user, record_id):
    try:
        workflow = TasksGroupAction()
        result = workflow.delete_task_group_action(record_id)

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to delete task group action',
                'error': result['error'],
                'success': False
            }), 400

        return jsonify({
            'message': 'Task Group Action deleted successfully',
            'data': {'record_id': record_id},
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
