from application.common.auth_middleware import token_required
from . import workflow_api_blueprint
from application.common.general import General
from flask import request, jsonify, abort
from ...models.workflow.instances import Instances
from ...models.workflow.tasks import Tasks
from ...models.workflow.task_dependencies import TaskDependencies
from ...models.workflow.process import Process
from datetime import datetime
import time
MAX_RETRIES = 3  # Maximum retries for task updates

"""API for start workflow instance."""
@workflow_api_blueprint.route('/api/start_workflow/<int:template_id>', methods=['PUT'])
@token_required
def start_workflow_instance(current_user, template_id):
    try:
        req = request.get_json(force=True)

        # Validate request
        req_validation = General.request_validation(json_data=req, keys=[["request_id", "required", None]])
        if req_validation:
            return jsonify({'message': 'Request parameter error', 'data': req_validation, 'success': False}), 400

        request_id = req.get('request_id')
        status = "Running"
        current_time = datetime.now()
        instance = Instances()
        # Check for existing instance with same request_id
        data = instance.exists(request_id=request_id)
        if data.get("success", False) is True and data.get("data") is not None:
            return jsonify(
                {'message': 'Duplicate request detected',
                 'error': 'Duplicate request detected',
                 'success': False}), 409

        # Create workflow instance
        result = instance.create_instance(template_id=template_id, request_id=request_id, status=status,
                                          started_at=current_time)

        if isinstance(result, dict) and 'error' in result:
            General.write_event(f"Failed to create workflow instance: {result['error']}")
            return jsonify(
                {'message': 'Failed to create workflow instance', 'error': result['error'], 'success': False}), 500

        instance_id = result.get("instance_id")
        General.write_event(f"Workflow instance {instance_id} created successfully.")

        # Get first task of the workflow
        task = Tasks()
        task_result = task.get_first_task_in_template(template_id=template_id)
        if isinstance(task_result, dict) and 'error' in task_result:
            General.write_event(f"Failed to retrieve first workflow task for template {template_id}: {task_result['error']}")
            return jsonify({'message': f'Failed to retrieve first workflow task for template {template_id}',
                            'error': task_result['error'], 'success': False}), 500

        first_step = task_result.get("task_id")
        if not first_step:
            return jsonify({'error': 'No steps defined for this workflow template', 'success': False}), 400

        # Get task information (assigned_to, group_id, level_id)
        task_info_result = task.get_task_info(task_id=first_step)
        if isinstance(task_info_result, dict) and 'error' in task_info_result:
            General.write_event(f"Failed to retrieve workflow task info for task {first_step}: {task_info_result['error']}")
            return jsonify({'message': f'Failed to retrieve workflow task info for task {first_step}',
                            'error': task_info_result['error'], 'success': False}), 500

        assigned_to = task_info_result.get("assigned_to")
        group_id = task_info_result.get("group_id")
        level_id = task_info_result.get("level_id")

        # Create workflow process for instance
        process = Process()
        process.create_process(instance_id=instance_id, task_id=first_step, status="Processing",
                               assigned_to=assigned_to, group_id=group_id, level_id=level_id)

        # Notify assigned user (if available)
        # if assigned_to:
        #     user = General.get_user_info(user_id=assigned_to)  # Assuming function exists to get user details
        #     if user:
        #         email = user.get("email")
        #         phone = user.get("phone")
        #         message = f"You have been assigned a new task (ID: {first_step}) in workflow {template_id}."
        #
        #         if email:
        #             send_email(email, "New Task Assigned", message)
        #         if phone:
        #             send_sms(phone, message)

        General.write_event(f"Workflow {template_id} started successfully with instance ID {instance_id}")

        return jsonify({'message': 'Workflow started', 'data': {'instance_id': instance_id}, 'success': True}), 201

    except Exception as e:
        General.write_event(f"An internal server error occurred: {str(e)}")
        return jsonify(
            {"error": "An internal server error occurred", "message": str(e), "data": None, "success": False}), 500
# @workflow_api_blueprint.route('/api/start_workflow/<int:template_id>', methods=['PUT'])
# @token_required
# def start_workflow_instance(current_user, template_id):
#     try:
#         req = request.get_json(force=True)
#         req_validation = General.request_validation(json_data=req, keys=[
#             ["request_id", "required", None],
#         ])
#
#         if req_validation is not None:
#             return jsonify({
#                 'message': 'Request parameter error',
#                 'data': req_validation,
#                 'success': False
#             }), 400
#
#         request_id = req.get('request_id')
#         status = "Running"
#         current_time = datetime.now()
#         instance = Instances()
#         result = instance.create_instance(template_id=template_id,
#                                           request_id=request_id,
#                                           status=status,
#                                           started_at=current_time)
#
#         if isinstance(result, dict) and 'error' in result:
#             return jsonify({
#                 'message': 'Failed to create workflow instance',
#                 'error': result['error'],
#                 'success': False
#             }), 500
#
#         """ get first task for specific workflow template"""
#         instance_id = result.get("instance_id")
#         task = Tasks()
#         task_result = task.get_first_task_in_template(template_id=template_id)
#         if isinstance(task_result, dict) and 'error' in task_result:
#             return jsonify({
#                 'message': f'Failed to Retrieve a first workflow task in specific template {template_id}',
#                 'error': task_result['error'],
#                 'success': False
#             }), 500
#
#         first_step = task_result.get("task_id")
#         if not first_step:
#             return jsonify({'error': 'No steps defined for this workflow template'}), 400
#
#         """ get task info group , level and assigned to"""
#         task_info_result = task.get_task_info(task_id=first_step)
#         if isinstance(task_info_result, dict) and 'error' in task_info_result:
#             return jsonify({
#                 'message': f'Failed to Retrieve workflow task info about group and level in '
#                            f'specific task {first_step}',
#                 'error': task_info_result['error'],
#                 'success': False
#             }), 500
#         assigned_to, group_id, level_id = None, None, None
#         if task_info_result:
#             assigned_to = task_info_result.get("assigned_to")
#             group_id = task_info_result.get("group_id")
#             level_id = task_info_result.get("level_id")
#
#         """ create workflow process for instance"""
#         process = Process()
#         process.create_process(instance_id=instance_id, task_id=first_step,
#                                status="Processing",
#                                assigned_to=assigned_to,
#                                group_id=group_id,
#                                level_id=level_id)
#         return jsonify({'message': 'Workflow started',
#                         'data': {'instance_id', instance_id},
#                         'success': True}), 201
#
#     except Exception as e:
#         return jsonify({
#             "error": "An internal server error occurred",
#             "message": str(e),
#             "data": None,
#             "success": False
#         }), 500

"""API for complete task."""
@workflow_api_blueprint.route('/api/complete_task/<int:process_id>', methods=['PUT'])
@token_required
def complete_task(current_user, process_id):
    try:
        req = request.get_json(force=True)

        # Validate request
        req_validation = General.request_validation(json_data=req, keys=[["task_id", "required", None]])
        if req_validation:
            return jsonify({'message': 'Request parameter error', 'data': req_validation, 'success': False}), 400

        task_id = req['task_id']
        General.write_event(f"Completing task {task_id} in process {process_id}", level="INFO")

        process = Process()

        # Retry mechanism for updating task status
        retries = 0
        while retries < MAX_RETRIES:
            try:
                result = process.update_process(process_id=process_id, status="Completed")
                if isinstance(result, dict) and 'error' in result:
                    raise Exception(result['error'])
                General.write_event(f"Task {task_id} marked as completed.")
                break
            except Exception as update_error:
                General.write_event(f"Error updating task {task_id}: {update_error}")
                retries += 1
                time.sleep(2)

        if retries == MAX_RETRIES:
            General.write_event(f"Task {task_id} could not be marked as completed after {MAX_RETRIES} attempts.")
            return jsonify({'message': 'Failed to update workflow process status', 'success': False}), 500

        # Get next tasks that depend on the completed task
        task_dependency = TaskDependencies()
        tasks_dependent = task_dependency.get_tasks_dependent_on_specific_task(task_id=task_id)

        # Get instance from process
        process_data = process.get_process_by_id(process_id=process_id)
        if isinstance(process_data, dict) and 'error' in process_data:
            return jsonify({'message': 'Failed to retrieve workflow process data', 'error': process_data['error'], 'success': False}), 500

        instance_id = process_data.get("instance_id")

        if tasks_dependent:
            General.write_event(f"Task {task_id} has dependent tasks: {tasks_dependent}")

            for dependent_task in tasks_dependent:
                next_task = dependent_task.get("next_task")

                # Check if this task has conditions from previous tasks
                specific_task_dependency = task_dependency.get_tasks_specific_task_depends(dependent_task_id=next_task)
                task_condition = specific_task_dependency.get("task_condition")

                if task_condition:  # Example: Waiting for all previous tasks to complete
                    General.write_event(f"Task {next_task} has a condition: {task_condition}")
                    # Implement condition check logic (e.g., ensure all dependencies are completed)

                # Get task info
                task = Tasks()
                task_info_result = task.get_task_info(task_id=next_task)
                if isinstance(task_info_result, dict) and 'error' in task_info_result:
                    return jsonify({
                        'message': f'Failed to retrieve workflow task info for task {next_task}',
                        'error': task_info_result['error'],
                        'success': False
                    }), 500

                assigned_to = task_info_result.get("assigned_to")
                group_id = task_info_result.get("group_id")
                level_id = task_info_result.get("level_id")
                # role_id = task_info_result.get("role_id")

                # Assign task to an available user if assigned_to is empty
                # if not assigned_to and role_id:
                #     assigned_to = get_available_user_by_role(role_id)

                # Create new task process
                process.create_process(instance_id=instance_id,
                                       task_id=next_task,
                                       status="Processing",
                                       assigned_to=assigned_to,
                                       group_id=group_id,
                                       level_id=level_id)

                # Send notifications
                # if assigned_to:
                #     notify_user(assigned_to, next_task)

            General.write_event(f"Task {task_id} completed, moving to next tasks.")
        else:
            # If no more tasks, mark the instance as completed
            instance = Instances()
            instance.update_instance_status(instance_id=instance_id, status="Completed")
            General.write_event(f"Workflow instance {instance_id} completed.")

        return jsonify({'message': 'Task completed and moved to the next step', 'data': None, 'success': True}), 200

    except Exception as e:
        General.write_event(f"An internal server error occurred: {str(e)}")
        return jsonify({"error": "An internal server error occurred", "message": str(e), "data": None, "success": False}), 500


# @workflow_api_blueprint.route('/api/complete_task/<int:process_id>', methods=['PUT'])
# @token_required
# def complete_task(current_user, process_id):
#     try:
#         req = request.get_json(force=True)
#         req_validation = General.request_validation(json_data=req, keys=[
#             ["task_id", "required", None],
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
#
#         process = Process()
#         result = process.update_process(process_id=process_id, status="Completed")
#
#         if isinstance(result, dict) and 'error' in result:
#             return jsonify({
#                 'message': 'Failed to update workflow process status',
#                 'error': result['error'],
#                 'success': False
#             }), 500
#
#         """ get next task for process"""
#         task_dependency = TaskDependencies()
#         tasks_dependent = task_dependency.get_tasks_dependent_on_specific_task(task_id=task_id)
#
#         """ get instance from process"""
#         process = Process()
#         process_data = process.get_process_by_id(process_id=process_id)
#         if isinstance(process_data, dict) and 'error' in result:
#             return jsonify({
#                 'message': 'Failed to update workflow process status',
#                 'error': process_data['error'],
#                 'success': False
#             }), 500
#         instance = process_data['data']
#         instance_id = instance.get("instance_id")
#
#         if tasks_dependent:
#             next_task = tasks_dependent.get("next_task")
#             """ check if more neext task then one"""
#             if len(tasks_dependent) > 1:
#                 """get previse task condetion"""
#                 specific_task_dependency = task_dependency.get_tasks_specific_task_depends(dependent_task_id=next_task)
#                 task_condition = specific_task_dependency.get("task_condition")
#                 """ execute depentend on previce task condition"""
#                 pass
#
#             else:
#                 """ get task info group , level and assigned to"""
#                 task = Tasks()
#                 task_info_result = task.get_task_info(task_id=next_task)
#                 if isinstance(task_info_result, dict) and 'error' in task_info_result:
#                     return jsonify({
#                         'message': f'Failed to Retrieve workflow task info about group and level in '
#                                    f'specific task  {next_task}',
#                         'error': task_info_result['error'],
#                         'success': False
#                     }), 500
#                 assigned_to, group_id, level_id = None, None, None
#                 if task_info_result:
#                     assigned_to = task_info_result.get("assigned_to")
#                     group_id = task_info_result.get("group_id")
#                     level_id = task_info_result.get("level_id")
#                 process.create_process(instance_id=instance_id,
#                                        task_id=next_task,
#                                        status="Processing",
#                                        assigned_to=assigned_to,
#                                        group_id=group_id,
#                                        level_id=level_id)
#
#         else:
#             instance = Instances()
#             instance.update_instance_status(instance_id=instance_id,status="Completed")
#
#         # Notify the assigned user
#         # notify_user(task_id)
#
#         return jsonify({'message': 'Task completed and moved to the next step',
#                         'data': None,
#                         'success': True}), 200
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
