from application.common.auth_middleware import token_required
from . import workflow_api_blueprint
from application.common.general import General
from flask import request, jsonify, abort
from ...models.workflow.templates import Templates
from ...models.workflow.tasks import Tasks
from ...models.workflow.task_dependencies import TaskDependencies
from ...models.workflow.automated_actions import AutomatedActions
from ...models.dynamic.forms import Forms
import json
from datetime import datetime

"""execute workflow template API."""
@workflow_api_blueprint.route('/api/workflows/templates/execute/<int:template_id>', methods=['GET'])
@token_required
def execute_workflow_template(current_user, template_id):
    try:
        # Begin database transaction
        try:
            now = datetime.now()
            # Update workflow template
            template = Templates()
            template_data = template.get_workflow_template_by_id(template_id)
            print(template_data)
            if isinstance(template_data, dict) and 'error' in template_data:
                # db.session.rollback()
                return jsonify({
                    'message': 'Failed to update workflow template',
                    'error': template_data['error'],
                    'success': False
                }), 500

            # Process nodes
            task = Tasks()
            form = Forms()
            node_task_map = {}
            data_diagram = template_data["data"]["diagram_json"]
            diagram_json = json.loads(data_diagram) if data_diagram else {}
            # print(diagram_json)
            if "nodes" in diagram_json and isinstance(diagram_json["nodes"], list):
                for node in diagram_json["nodes"]:
                    task_data = node.get("data", {})
                    if not all(k in task_data for k in ["role", "group", "form_name", "form_fields"]):
                        General.write_event(f"Skipping node due to missing required fields: {node}", level="warning")
                        continue

                    insert_task = task.create_task(
                        template_id=template_id,
                        name=node.get("label", "Unnamed Task"),
                        assigned_role=int(task_data.get("role", 0)) if task_data.get("role") else None,
                        task_type=task_data.get("type", "manual"),
                        assigned_to=int(task_data.get("group", 0)) if task_data.get("group") else None,
                        created_at=now
                    )

                    if isinstance(insert_task, dict) and 'error' in insert_task:
                        return jsonify({
                            'message': 'Failed to create workflow template tasks',
                            'error': insert_task['error'],
                            'success': False
                        }), 500

                    """ اذا كان نو المهمة يدوية يتم انشاء نموذج لتطبيق نوع المهمة"""
                    task_type = task_data.get("type")
                    if task_type == "manual":
                        """ create form and assign group for inserted task """
                        if insert_task and "task_id" in insert_task:
                            node_task_map[node["id"]] = insert_task["task_id"]
                            """ create task """
                            form.create_form_with_fields(
                                task_id=insert_task["task_id"],
                                form_name=task_data["form_name"],
                                description=None,
                                fields=task_data["form_fields"]
                            )
                            """ assign task to group """
                            task.assign_task_group(task_id=insert_task["task_id"],
                                                   group_id=task_data["group"],
                                                   level_id=task_data["level"])

                    else:
                        """ assign task to automated actions"""
                        action = AutomatedActions()
                        action.create_automated_action(task_id=insert_task["task_id"],
                                                       action_type=task_type,
                                                       action_config=task_data["config"])

            # Process edges
            depended = TaskDependencies()
            if "edges" in diagram_json and isinstance(diagram_json["edges"], list):
                for edge in diagram_json["edges"]:
                    source_task = node_task_map.get(edge.get("source"))
                    target_task = node_task_map.get(edge.get("target"))

                    if source_task and target_task:
                        depended.create_task_dependence(
                            template_id=template_id,
                            task_id=source_task,
                            dependent_task_id=target_task,
                            task_condition=None
                        )

        except Exception as e:
            General.write_event(f"Database transaction failed: {str(e)}", level="error")
            return jsonify({
                "message": "Database transaction error",
                "error": str(e),
                "success": False
            }), 500

        """ if all is done then change execute to true in template"""
        execute_status = template.execute_workflow_template_done(template_id=template_id)
        if isinstance(execute_status, dict) and 'error' in execute_status:
            return jsonify({
                'message': 'Failed to change execute to done, but affected data successfully',
                'error': execute_status['error'],
                'success': False
            }), 500

        return jsonify({
            'message': execute_status["message"],
            'data': diagram_json,
            'success': True
        }), 200

    except Exception as e:
        General.write_event(f"Unexpected error in update_workflow_template: {str(e)}", level="error")
        return jsonify({
            "message": "An internal server error occurred",
            "error": str(e),
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
