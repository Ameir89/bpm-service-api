from application.common.auth_middleware import token_required
from . import workflow_api_blueprint
from application.common.general import General
from flask import request, jsonify, abort
from ...models.workflow.task_group_workflow import TasksGroupWorkflow

"""create task group workflow API."""
@workflow_api_blueprint.route('/api/workflows/task_group_workflow/<int:task_id>', methods=['POST'])
@token_required
def create_task_group_workflow(current_user,task_id):
    try:
        # 
        req = request.get_json(force=True)

        # Expecting a list of objects
        if not isinstance(req, list):
            return jsonify({
                'message': 'Invalid data format: expected a list of objects.',
                'success': False
            }), 400

        data = []
        for item in req:
            # Validate required fieldsass
            if not all(k in item for k in ("from_group", "to_group", "assign_task")):
                return jsonify({
                    'message': 'Missing required fields in some items.',
                    'success': False
                }), 400
            
            data.append({
                "task_id": task_id,
                "from_group": item["from_group"],
                "to_group": item["to_group"],
                "assign_task": item["assign_task"]
            })

        workflow = TasksGroupWorkflow()

        try:
            result = workflow.create_task_group_workflow(data)
        except Exception as db_error:
            # Catch unexpected errors inside the function
            return jsonify({
                'message': 'Error while creating task group workflows.',
                'error': str(db_error),
                'success': False
            }), 500

         # Expecting: {'inserted_ids': 2, 'success': True}
        if not (isinstance(result, dict) and result.get("success") is True):
            return jsonify({
                'message': 'Unexpected response from create task group workflow.',
                'error': str(result),
                'success': False
            }), 500

        # Format response output
        response_data = [
            {"from_group": item["from_group"], "to_group": item["to_group"], "assign_task": item["assign_task"]}
            for item in data
        ]
        
        return jsonify({
            'message': 'Task group workflow added successfully',
            'data': response_data,
            'success': True
        }), 200
        

    except Exception as e:
        return jsonify({
            "error": "An internal server error occurred",
            "message": str(e),
            "success": False
        }), 500


"""update workflow API."""
@workflow_api_blueprint.route('/api/workflows/task_group_workflow/<int:record_id>', methods=['PUT'])
@token_required
def update_task_group_workflow(current_user, record_id):
    try:
        req = request.get_json(force=True)
        req_validation = General.request_validation(json_data=req, keys=[
            ["task_id", "required", None],
            ["from_group", "required", None],
            ["to_group", "required", None],
            ["assign_task", "required", None]
        ])

        if req_validation is not None:
            return jsonify({
                'message': 'Request parameter error',
                'data': req_validation,
                'success': False
            }), 400

        task_id = req['task_id']
        from_group = req['from_group']
        to_group = req['to_group']
        assign_task = req['assign_task']

        workflow = TasksGroupWorkflow()
        result = workflow.update_task_group_workflow(record_id, task_id, from_group, to_group, assign_task)

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


"""get task group workflow by id API."""
@workflow_api_blueprint.route('/api/workflows/task_group_workflow/<int:task_id>', methods=['GET'])
@token_required
def get_task_group_workflow(current_user, task_id):
    try:
        workflow = TasksGroupWorkflow()
        result = workflow.get_task_group_workflow(task_id)

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to retrieve task group workflow info',
                'error': result['error'],
                'success': False
            }), 404

        return jsonify({
            'message': 'Successfully retrieved task group workflow',
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
@workflow_api_blueprint.route('/api/workflows/task_group_workflow/<int:record_id>', methods=['DELETE'])
@token_required
def delete_task_group_workflow(current_user, record_id):
    try:
        workflow = TasksGroupWorkflow()
        result = workflow.delete_task_group_workflow(record_id)

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to delete workflow',
                'error': result['error'],
                'success': False
            }), 400

        return jsonify({
            'message': 'Task Group Workflow deleted successfully',
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
