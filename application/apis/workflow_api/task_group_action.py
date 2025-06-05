from application.common.auth_middleware import token_required
from . import workflow_api_blueprint
from application.common.general import General
from flask import request, jsonify, abort
from ...models.workflow.task_group_action import TasksGroupAction

# logger = logging.getLogger(__name__)
"""create task group workflow API."""

@workflow_api_blueprint.route('/api/workflows/task_group_action/<int:task_id>', methods=['POST'])
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
        
        return jsonify({
            'message': 'Task group action added successfully',
            'data': response_data,
            'success': True
        }), 200

    except Exception as e:
        return jsonify({
            "error": "An internal server error occurred",
            "message": str(e),
            "success": False
        }), 500

# """update workflow API."""
@workflow_api_blueprint.route('/api/workflows/task_group_action/<int:task_id>', methods=['PUT'])
@token_required
def update_task_group_action(current_user, task_id):
    try:
        req_data = request.get_json(force=True)

        if not isinstance(req_data, list):
            return jsonify({
                'message': 'Invalid data format: expected a list of objects.',
                'success': False
            }), 400

        workflow = TasksGroupAction()

        # 1. حذف الإجراءات الحالية المرتبطة بالمهمة
        result_data = workflow.get_task_group_action(task_id)
        # print(f"Get task group action result: {result_data}")
        General.write_event(f"Get task group action result: {result_data}", "INFO")

        existing_actions = result_data.get('data') if isinstance(result_data, dict) else []

        if isinstance(existing_actions, list):
            for item in existing_actions:
                item_id = item.get("id")
                if item_id:
                    delete_result = workflow.delete_task_group_action(item_id)
                    if delete_result.get("success") is not True:
                        General.write_event(f"Failed to delete item {item_id}: {delete_result.get('error')}")
        else:
            General.write_event("No valid list of existing actions found.", "INFO")

        # 2. التحقق من صحة البيانات الجديدة
        new_actions = []
        for item in req_data:
            if not all(k in item for k in ("group_id", "action", "level")):
                return jsonify({
                    'message': 'Missing required fields in some items. Required: group_id, action, level',
                    'success': False
                }), 400

            new_actions.append({
                "task_id": task_id,
                "group_id": item["group_id"],
                "action": item["action"],
                "level": item["level"]
            })

        # 3. إدخال البيانات الجديدة
        try:
            result = workflow.create_task_group_action(new_actions)
        except Exception as db_error:
            General.write_event(f"Exception during creation: {str(db_error)}")
            return jsonify({
                'message': 'Error while creating task group actions.',
                'error': str(db_error),
                'success': False
            }), 500

        if isinstance(result, dict) and result.get('success') is not True:
            return jsonify({
                'message': 'Failed to create task group actions',
                'error': result.get('error'),
                'success': False
            }), 500

        return jsonify({
            'message': 'Task group action updated successfully',
            'data': result,
            'success': True
        }), 200

    except Exception as e:
        General.write_event(f"Unexpected error in update_task_group_action: {str(e)}")
        return jsonify({
            "error": "An internal server error occurred",
            "message": str(e),
            "data": None,
            "success": False
        }), 500

        
# @workflow_api_blueprint.route('/api/workflows/task_group_action/<int:task_id>', methods=['PUT'])
# @token_required
# def update_task_group_action(current_user, task_id):
#     """
#     Update task group actions for a specific task.
    
#     Args:
#         current_user: Authenticated user object
#         task_id (int): ID of the task to update
        
#     Expected JSON payload:
#         List of objects with fields: group_id, action, level, record_id (optional)
        
#     Returns:
#         JSON response with success/error status and data
#     """
#     try:
#         # Validate task_id
#         if task_id <= 0:
#             return jsonify({
#                 'message': 'Invalid task ID provided.',
#                 'success': False
#             }), 400
            
#         # Get and validate request data
#         try:
#             req = request.get_json(force=True)
#         except Exception as json_error:
#             General.write_event(f"Invalid JSON in request: {json_error}")
#             return jsonify({
#                 'message': 'Invalid JSON format in request body.',
#                 'success': False
#             }), 400
        
#         # Validate data structure
#         if not isinstance(req, list):
#             return jsonify({
#                 'message': 'Invalid data format: expected a list of objects.',
#                 'success': False
#             }), 400
            
#         if not req:  # Empty list
#             return jsonify({
#                 'message': 'No data provided for update.',
#                 'success': False
#             }), 400
        
#         # Validate each item in the list
#         required_fields = ["group_id", "action", "level"]
#         validated_items = []
        
#         for index, item in enumerate(req):
#             if not isinstance(item, dict):
#                 return jsonify({
#                     'message': f'Item at index {index} is not a valid object.',
#                     'success': False
#                 }), 400
            
#             # Check required fields
#             missing_fields = [field for field in required_fields if field not in item or item[field] is None]
#             if missing_fields:
#                 return jsonify({
#                     'message': f'Missing required fields in item {index}: {", ".join(missing_fields)}',
#                     'success': False
#                 }), 400
            
#             # Validate field types and values
#             try:
#                 group_id = int(item["group_id"])
#                 level = int(item["level"])
#                 action = str(item["action"]).strip()
#                 record_id = item.get("id")
                
#                 if group_id <= 0:
#                     return jsonify({
#                         'message': f'Invalid group_id in item {index}: must be positive integer.',
#                         'success': False
#                     }), 400
                
#                 if not action:
#                     return jsonify({
#                         'message': f'Invalid action in item {index}: cannot be empty.',
#                         'success': False
#                     }), 400
                
#                 if record_id is not None:
#                     record_id = int(record_id)
#                     if record_id <= 0:
#                         return jsonify({
#                             'message': f'Invalid record_id in item {index}: must be positive integer.',
#                             'success': False
#                         }), 400
                
#                 validated_items.append({
#                     'record_id': record_id,
#                     'group_id': group_id,
#                     'action': action,
#                     'level': level
#                 })
                
#             except (ValueError, TypeError) as validation_error:
#                 return jsonify({
#                     'message': f'Invalid data types in item {index}: {str(validation_error)}',
#                     'success': False
#                 }), 400
        
#         # Initialize workflow handler
#         try:
#             workflow = TasksGroupAction()
#         except Exception as init_error:
#             General.write_event(f"Failed to initialize TasksGroupAction: {init_error}")
#             return jsonify({
#                 'message': 'Failed to initialize workflow handler.',
#                 'success': False
#             }), 500
        
#         # Process updates
#         results = []
#         errors = []
        
#         for index, item in enumerate(validated_items):
#             try:
#                 result = workflow.update_task_group_action(
#                     record_id=item['id'],
#                     task_id=task_id,
#                     group_id=item['group_id'],
#                     action=item['action'],
#                     level=item['level']
#                 )
                
#                 # Handle error results from the workflow method
#                 if isinstance(result, dict) and 'error' in result:
#                     error_msg = f"Item {index}: {result['error']}"
#                     errors.append(error_msg)
#                     General.write_event(f"Workflow update error for task {task_id}: {error_msg}")
#                 else:
#                     results.append({
#                         'index': index,
#                         'result': result,
#                         'item': item
#                     })
                    
#             except Exception as update_error:
#                 error_msg = f"Item {index}: {str(update_error)}"
#                 errors.append(error_msg)
#                 General.write_event(f"Exception during workflow update for task {task_id}: {update_error}")
        
#         # Determine response based on results
#         if errors and not results:
#             # All updates failed
#             return jsonify({
#                 'message': 'All task group action updates failed.',
#                 'errors': errors,
#                 'success': False
#             }), 500
            
#         elif errors and results:
#             # Partial success
#             return jsonify({
#                 'message': f'Partial success: {len(results)} updates succeeded, {len(errors)} failed.',
#                 'data': results,
#                 'errors': errors,
#                 'success': True,
#                 'partial': True
#             }), 207  # Multi-Status
            
#         else:
#             # All updates successful
#             General.write_event(f"Successfully updated {len(results)} task group actions for task {task_id}", level='INFO')
#             return jsonify({
#                 'message': f'Successfully updated {len(results)} task group action(s).',
#                 'data': results,
#                 'success': True
#             }), 200
            
#     except Exception as e:
#         # Log the full exception for debugging
#         General.write_event(f"Unexpected error in update_task_group_action for task {task_id}: {str(e)}", exc_info=True)
        
#         return jsonify({
#             'message': 'An internal server error occurred while processing the request.',
#             'error': str(e),
#             'success': False
#         }), 500


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
