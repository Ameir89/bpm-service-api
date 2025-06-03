from application.mysql_connection import Connection
from application.common.general import General


class TasksGroupAction:
    def __init__(self):
        self.db_connection = Connection()

    """
        Create a new task group action.
    """

    def create_task_group_action(self, data_list):
        if not data_list or not isinstance(data_list, list):
            return {"error": "Data list is required and must be a list of dictionaries.", "success": False}

        try:
            inserted_ids = self.db_connection.create_many("`task_group_action`", data_list, debug=True)

            if not inserted_ids:
                return {"error": "Failed to create task group actions.", "success": False}

            return {"inserted_ids": inserted_ids, "success": True}
        except Exception as e:
            General.write_event(f"Error creating task group actions: {str(e)}")
            return {"error": f"Error creating task group actions: {str(e)}", "success": False}

    """
    Function use to get all task group action
    """
    def get_all_task_group_actions(self):
        try:
            query = "SELECT * FROM `task_group_action`"
            result = self.db_connection.select(query=query)
            if not result:
                return {"data": None, "success": False}
            return {"data": result, "success": True}
        except Exception as e:
            General.write_event(f"Error retrieving all task group actions: {str(e)}")
            return {"error": f"Error retrieving all task group actions: {str(e)}", "success": False}
        
    def get_task_group_action(self, task_id):
        """
        Retrieve task group actions associated with a given task ID.
        Returns joined data with group names.
        """
        # Validate task_id
        if not isinstance(task_id, int) or task_id <= 0:
            return {
                "error": "Invalid task ID provided.",
                "success": False
            }

        # Check if task_id is provided
        if not task_id:
            return {
                "error": "Task ID is required.",
                "success": False
            }

        try:
            # Construct query to fetch task group actions with group name
            query = """
                SELECT tg.*, g.group_name 
                FROM task_group_action tg
                LEFT JOIN `groups` g ON g.group_id = tg.group_id
                WHERE tg.task_id = %s
            """

            # Execute query
            result = self.db_connection._execute_query(
                query=query,
                bind_variables=(task_id,)
            )

            if not result:
                return {
                    "data": None,
                    "message": f"No task group actions found for task_id {task_id}.",
                    "success": False
                }

            return {
                "data": result,
                "success": True
            }

        except Exception as e:
            # Log the error
            General.write_event(f"Error retrieving task group actions: {str(e)}")

            return {
                "error": f"Error retrieving task group actions: {str(e)}",
                "success": False
            }

    
    """
    function update to update task group action
    """

    def update_task_group_action(self, id, task_id, group, action, level):
        if not id or not task_id or not group or not action or not level:
            return {"error": "task ID or group or action or level is required.", "success": False}

        try:
            update_data = {
                "id": id,
                "task_id": task_id,
                "`group`": group,
                "`action`": action,
                "`level`": level,
            }
            is_update = self.db_connection.update(
                table_name="`task_group_action`",
                condition_column="id",
                condition_value=id,
                update_data=update_data
            )

            if is_update != 0:
                return {"error": "Failed to update task group action.", "success": False}

            return {"success": True, "message": "task group action updated successfully."}
        except Exception as e:
            General.write_event(f"Error update task group action: {str(e)}")
            return {"error": f"Error update task group action: {str(e)}", "success": False}

    """
    Deletes a task group action by ID.
    """
    def delete_task_group_action(self, id):
        if not id:
            return {"error": "Task ID is required.", "success": False}

        try:
            deleted_count = self.db_connection.delete(
                table_name="`task_group_action`",
                condition="id = %s",
                bind_variables=(id,)
            )

            if deleted_count == 0:
                return {"error": "No task found with the given ID.", "success": False}

            return {"success": True, "message": "Task deleted successfully."}

        except Exception as e:
            General.write_event(f"Error deleting task group workflow with ID {id}: {str(e)}")
            return {"error": "An error occurred while deleting the task.", "success": False}

