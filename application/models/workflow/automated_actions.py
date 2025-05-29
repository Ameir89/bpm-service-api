from application.mysql_connection import Connection
from application.common.general import General


class AutomatedActions:
    def __init__(self):
        self.db_connection = Connection()

    def create_automated_action(self, task_id, action_type, action_config):
        """ function to create automated action ."""
        if not task_id or not action_type or not action_config:
            return {"error": "Task task_id ,action_type,  action_config are required.", "success": False}

        try:
            data = {
                "task_id": task_id,
                "action_type": action_type,
                "action_config": action_config,
            }

            action_id = self.db_connection.create("`automated_actions`", data, debug=True)

            if not action_id:
                return {"error": "Failed to create task automated action.", "success": False}

            return {"action_id": action_id, "success": True}
        except Exception as e:
            General.write_event(f"Error creating task automated action: {str(e)}")
            return {"error": f"Error creating task automated action: {str(e)}", "success": False}

    def get_automated_action_task(self, task_id):
        """ Retrieve automated action data for specific task. """
        if not task_id:
            return {"error": "task ID is required.", "success": False}

        try:
            query = 'SELECT * FROM automated_actions WHERE task_id = %s and is_deleted = %s '
            bind_variables = (task_id, 0)
            result = self.db_connection.execute_raw(query=query,
                                                    bind_variables=bind_variables)

            if not result:
                return {"data": None, "success": False}

            return {"data": result, "success": True}
        except Exception as e:
            General.write_event(f"Error Retrieve automated action data for specific task: {str(e)}")
            return {"error": f"Error Retrieve automated action data for specific task: {str(e)}", "success": True}

    def delete_automated_action_task(self, action_id):
        """ delete automated action task. """
        if not action_id:
            return {"error": "action id is required.", "success": False}

        try:
            is_update = self.db_connection.update(
                table_name="`automated_actions`",
                condition_column="id",
                condition_value=action_id,
                update_data={"is_deleted": True}
            )

            if is_update != 0:
                return {"error": "Failed to delete automated action task.", "success": False}

            return {"success": True, "message": "successfully delete automated action task."}
        except Exception as e:
            General.write_event(f"Error delete automated action task: {str(e)}")
            return {"error": f"Error while delete automated action task: {str(e)}", "success": False}