from typing import Dict, Any, Optional, List
from application.mysql_connection import Connection
from application.common.general import General
from application.models.workflow.tasks import Tasks

class Workflows:
    def __init__(self):
        self.db_connection = Connection()
        self.logger = General  # Assuming General.write_event is used for logging

    def create_workflow(self, label: str, name: str, description: str, status: str, created_by: int) -> Dict[str, Any]:
        """
        Create a new workflow along with start and end tasks.
        Returns success dict or error message.
        """
        if not all([label, name, created_by]):
            return {"error": "Label, name, and created_by are required.", "success": False}

        try:
            data = {
                "label": label,
                "name": name,
                "description": description,
                "status": status,
                "created_by": created_by
            }

            workflow_id = self.db_connection.create("workflows", data, debug=True)

            if not workflow_id:
                self.logger.write_event("Failed to insert workflow into database")
                return {"error": "Failed to create workflow.", "success": False}

            task_manager = Tasks()

            start_task = task_manager.create_task(workflow_id=workflow_id,
                                                  name='Start Task',
                                                  task_type='start')
            end_task = task_manager.create_task(workflow_id=workflow_id,
                                                name='End Task',
                                                task_type='end')

            if not start_task.get("success"):
                self.logger.write_event(f"Failed to create start task for workflow ID {workflow_id}")
                delete_result = self.delete_workflow(workflow_id)
                if not delete_result.get("success"):
                    self.logger.write_event(f"Failed to rollback workflow deletion after failure: {workflow_id}")
                return {"error": "Failed to create start task.", "success": False}

            if not end_task.get("success"):
                self.logger.write_event(f"Failed to create end task for workflow ID {workflow_id}")
                delete_result = self.delete_workflow(workflow_id)
                if not delete_result.get("success"):
                    self.logger.write_event(f"Failed to rollback workflow deletion after failure: {workflow_id}")
                return {"error": "Failed to create end task.", "success": False}

            return {"workflow_id": workflow_id, "success": True}

        except Exception as e:
            self.logger.write_event(f"Exception occurred while creating workflow: {str(e)}")
            return {"error": f"Error creating workflow: {str(e)}", "success": False}

    def get_workflow(self, workflow_id: int) -> Dict[str, Any]:
        """
        Retrieve a workflow by ID including its associated template.
        """
        if not workflow_id:
            return {"error": "Workflow ID is required.", "success": False}

        try:
            query = """
                SELECT w.*
                FROM workflows w 
                WHERE w.id = %s AND w.is_deleted = %s AND w.status = %s
            """
            bind_variables = (workflow_id, 0, 1,)
            result = self.db_connection.execute_raw(query, bind_variables)

            if not result:
                return {"error": "Workflow not found.", "success": False}
            return {"data": result[0], "success": True}  # assuming result is list
        except Exception as e:
            self.logger.write_event(f"Error retrieving workflow: {str(e)}")
            return {"error": f"Error retrieving workflow: {str(e)}", "success": False}

    def list_workflows(self, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        Retrieve workflows with pagination and include template info.
        """
        try:
            offset = (page - 1) * page_size
            base_query = """
                FROM workflows w  
                WHERE  w.is_deleted = %s AND w.status = %s
            """
            bind_vars = (0, 1)

            # Get paginated data
            query = f"""
                SELECT w.* 
                {base_query}
                LIMIT %s OFFSET %s
            """
            results = self.db_connection.execute_raw(query, (*bind_vars, page_size, offset))

            # Count total records
            count_query = f"SELECT COUNT(*) as total {base_query}"
            total_count_result = self.db_connection.execute_raw(count_query, bind_vars)
            total_count = total_count_result[0]['total'] if total_count_result else 0

            return {
                "data": results,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_items": total_count,
                    "total_pages": (total_count + page_size - 1) // page_size
                },
                "success": True
            }

        except Exception as e:
            self.logger.write_event(f"Error listing workflows: {str(e)}")
            return {"error": f"Error listing workflows: {str(e)}", "success": False}

    def change_workflow_status(self, workflow_id: int, status: int) -> Dict[str, Any]:
        """
        Change the status of a workflow (0 = inactive, 1 = active).
        """
        if not workflow_id:
            return {"error": "Workflow ID is required.", "success": False}
        if status not in [0, 1]:
            return {"error": "Status must be 0 or 1.", "success": False}

        try:
            updated = self.db_connection.update(
                table_name="workflows",
                condition_column="id",
                condition_value=workflow_id,
                update_data={"status": status},
                debug=True
            )
            if not updated:
                return {"error": "Failed to update workflow status.", "success": False}
            return {"message": "Workflow status updated successfully.", "success": True}
        except Exception as e:
            self.logger.write_event(f"Error changing workflow status: {str(e)}")
            return {"error": f"Error updating workflow status: {str(e)}", "success": False}

    def update_workflow_data(self, label: str, name: str, description: str, status: int, workflow_id: int) -> Dict[str, Any]:
        """
        Update existing workflow data.
        """
        if not all([label, name, description, workflow_id]):
            return {"error": "All fields except status are required.", "success": False}

        try:
            updated = self.db_connection.update(
                table_name="workflows",
                condition_column="id",
                condition_value=workflow_id,
                update_data={
                    "label": label,
                    "name": name,
                    "description": description,
                    "status": status
                }
            )
            if not updated:
                return {"error": "Failed to update workflow data.", "success": False}
            return {"message": "Workflow data updated successfully.", "success": True}
        except Exception as e:
            self.logger.write_event(f"Error updating workflow data: {str(e)}")
            return {"error": f"Error updating workflow: {str(e)}", "success": False}

    def delete_workflow(self, workflow_id: int) -> Dict[str, Any]:
        """
        Soft-delete a workflow.
        """
        if not workflow_id:
            return {"error": "Workflow ID is required.", "success": False}

        try:
            updated = self.db_connection.update(
                table_name="workflows",
                condition_column="id",
                condition_value=workflow_id,
                update_data={"is_deleted": True}
            )
            if not updated:
                return {"error": "Failed to soft-delete workflow.", "success": False}
            return {"message": "Workflow deleted (soft-deleted).", "success": True}
        except Exception as e:
            self.logger.write_event(f"Error deleting workflow: {str(e)}")
            return {"error": f"Error deleting workflow: {str(e)}", "success": False}