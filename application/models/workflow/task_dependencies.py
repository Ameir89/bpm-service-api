from application.mysql_connection import Connection
from application.common.general import General

class TaskDependencies:
    def __init__(self):
        self.db_connection = Connection()

    def create_task_dependence(self, template_id, task_id, dependent_task_id,  task_condition):
        """ function to create tasks dependent ."""
        if not template_id or not task_id or not dependent_task_id:
            return {"error": "Task name , template id ,task_id , dependent_task_id are required.", "success": False}

        try:
            data = {
                "template_id": template_id,
                "task_id": task_id,
                "dependent_task_id": dependent_task_id,
                "task_condition": task_condition,
            }

            dependent_id = self.db_connection.create("`task_dependencies`", data, debug=True)
            
            if not dependent_id:
                return {"error": "Failed to create  task relation.", "success": False}

            return {"dependent_id": dependent_id, "success": True}
        except Exception as e:
            General.write_event(f"Error creating task dependence: {str(e)}")
            return {"error": f"Error creating task dependence: {str(e)}", "success": False}

    def get_tasks_dependent_on_specific_task(self, task_id):
        """ Retrieve all tasks dependent on a specific task. """
        if not task_id:
            return {"error": "template ID is required.", "success": False}

        try:
            query = ('SELECT t.id as next_task,t.template_id,t.name,t.task_type, '
                     't.assigned_role, t.assigned_to , td.task_condition '
                     'FROM workflow_tasks t '
                     'JOIN task_dependencies td ON t.id = td.dependent_task_id '
                     'WHERE td.task_id = %s and t.is_deleted = %s ')
            bind_variables = (task_id, 0)
            result = self.db_connection.execute_raw(query=query,
                                                    bind_variables=bind_variables)

            if not result:
                return {"data": None, "success": False}

            return {"data": result, "success": True}
        except Exception as e:
            General.write_event(f"Error retrieving all tasks dependent on a specific task: {str(e)}")
            return {"error": f"Error retrieving all tasks dependent on a specific task: {str(e)}", "success": True}

    def get_tasks_specific_task_depends(self, dependent_task_id):
        """ Retrieve all tasks that a specific task depends on. """
        if not dependent_task_id:
            return {"error": "dependent_task_id is required.", "success": False}

        try:
            query = ('SELECT t.id as task_id, t.template_id,t.name,t.task_type, '
                     't.assigned_role, t.assigned_to , td.task_condition'
                     'FROM workflow_tasks t '
                     'JOIN task_dependencies td ON t.id = td.task_id '
                     'WHERE td.dependent_task_id  = %s and t.is_deleted = %s ')
            bind_variables = (dependent_task_id, 0)
            result = self.db_connection.execute_raw(query=query,
                                                    bind_variables=bind_variables)

            if not result:
                return {"data": None, "success": False}

            return {"data": result, "success": True}
        except Exception as e:
            General.write_event(f"Error retrieving all tasks that a specific task depends on: {str(e)}")
            return {"error": f"Error all tasks that a specific task depends on: {str(e)}", "success": True}

    def delete_task_dependence(self, dependent_id):
        """ delete task dependence. """
        if not dependent_id:
            return {"error": "dependent id is required.", "success": False}

        try:
            is_update = self.db_connection.update(
                table_name="`task_dependencies`",
                condition_column="id",
                condition_value=dependent_id,
                update_data={"is_deleted": True}
            )

            if is_update != 0:
                return {"error": "Failed to delete task dependencies.", "success": False}

            return {"success": True, "message": "successfully delete task dependencies."}
        except Exception as e:
            General.write_event(f"Error delete task dependencies: {str(e)}")
            return {"error": f"Error while delete task dependencies: {str(e)}", "success": False}
