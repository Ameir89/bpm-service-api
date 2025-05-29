from application.mysql_connection import Connection
from application.common.general import General


class TasksGroupWorkflow:
    def __init__(self):
        self.db_connection = Connection()

    """
        Create a new task group workflow.
    """

    # def create_task_group_workflow(self, task_id, from_group, to_group):
    #     if not task_id or not from_group or not to_group:
    #         return {"error": "Task task_id , from_group ,to_group  are required.",
    #                 "success": False}
    #
    #     try:
    #         data = {
    #             "task_id": task_id,
    #             "from_group": from_group,
    #             "to_group": to_group
    #         }
    #
    #         task_id = self.db_connection.create_many("`task_group_workflow`", data, debug=True)
    #         # print(task_id)
    #         if not task_id:
    #             return {"error": "Failed to create task group workflow.", "success": False}
    #
    #         return {"task_id": task_id, "success": True}
    #     except Exception as e:
    #         General.write_event(f"Error creating task group workflow: {str(e)}")
    #         return {"error": f"Error creating task group workflow: {str(e)}", "success": False}
    def create_task_group_workflow(self, data_list):
        if not data_list or not isinstance(data_list, list):
            return {"error": "Data list is required and must be a list of dictionaries.", "success": False}

        try:
            inserted_ids = self.db_connection.create_many("`task_group_workflow`", data_list, debug=True)

            if not inserted_ids:
                return {"error": "Failed to create task group workflows.", "success": False}

            return {"inserted_ids": inserted_ids, "success": True}
        except Exception as e:
            General.write_event(f"Error creating task group workflows: {str(e)}")
            return {"error": f"Error creating task group workflows: {str(e)}", "success": False}

    """
    Function use to get all task for template
    """
    def get_task_group_workflow(self, task_id):
        """
        Retrieve a workflow's tasks for templates.
        """
        if not task_id:
            return {"error": "Task ID is required.", "success": False}

        try:

            result = self.db_connection.select(table_name='`task_group_workflow`',
                                               condition='task_id = %s',
                                               bind_variables=(task_id,))
            if not result:
                return {"data": None, "success": False}

            return {"data": result, "success": True}
        except Exception as e:
            General.write_event(f"Error retrieving task group workflow: {str(e)}")
            return {"error": f"Error retrieving group workflow: {str(e)}", "success": True}

    """
    function update to workflow task data 
    """

    def update_task_group_workflow(self, id, task_id, from_group, to_group, assign_task):
        if not id or not task_id or not from_group or not to_group or not assign_task:
            return {"error": "task ID is required.", "success": False}

        try:
            update_data = {
                "id": id,
                "task_id": task_id,
                "from_group": from_group,
                "to_group": to_group,
                "assign_task": assign_task
            }
            is_update = self.db_connection.update(
                table_name="`task_group_workflow`",
                condition_column="id",
                condition_value=id,
                update_data=update_data
            )

            if is_update != 0:
                return {"error": "Failed to update task group workflow.", "success": False}

            return {"success": True, "message": "task updated successfully."}
        except Exception as e:
            General.write_event(f"Error update task group workflow: {str(e)}")
            return {"error": f"Error update task group workflow: {str(e)}", "success": False}

    """
    Deletes a task group workflow by ID.
    """
    def delete_task_group_workflow(self, id):
        if not id:
            return {"error": "Task ID is required.", "success": False}

        try:
            deleted_count = self.db_connection.delete(
                table_name="`task_group_workflow`",
                condition="id = %s",
                bind_variables=(id,)
            )

            if deleted_count == 0:
                return {"error": "No task found with the given ID.", "success": False}

            return {"success": True, "message": "Task deleted successfully."}

        except Exception as e:
            General.write_event(f"Error deleting task group workflow with ID {id}: {str(e)}")
            return {"error": "An error occurred while deleting the task.", "success": False}

