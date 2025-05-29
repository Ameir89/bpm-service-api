from application.mysql_connection import Connection
from application.common.general import General


class Tasks:
    def __init__(self):
        self.db_connection = Connection()
    
    
    """
        Create a new worflow task.
    """
    def create_task(self, workflow_id, name, assigned_role=None, task_type=None, assigned_to=None):
        if not workflow_id or not name :
            return {"error": "Task name , workflow_id   are required.",
                    "success": False}

        try:
            data = {
                "workflow_id": workflow_id,
                "name": name,
                "task_type": task_type,
            }

            task_id = self.db_connection.create("`workflow_tasks`", data, debug=True)
            print(task_id)
            if not task_id:
                return {"error": "Failed to create workflow tasks.", "success": False}

            return {"task_id": task_id, "success": True}
        except Exception as e:
            General.write_event(f"Error creating workflow task: {str(e)}")
            return {"error": f"Error creating workflow task: {str(e)}" , "success":False}
        

    """
    Function use to get all task for template
    """   
    def get_all_tasks(self, workflow_id):
        """
        Retrieve a tasks for workflow.
        """
        if not workflow_id:
            return {"error": "workflow ID is required.", "success": False}

        try:
            
            result = self.db_connection.select(table_name='`workflow_tasks`',
                                               condition='workflow_id = %s AND is_deleted = %s',
                                               bind_variables=(workflow_id, 0,))
            if not result:
                return {"data": None, "success": False}

            return {"data": result, "success": True}
        except Exception as e:
            General.write_event(f"Error creating workflow task: {str(e)}")
            return {"error": f"Error retrieving workflow tasks: {str(e)}" , "success" : True}
    
    
    """
    Function use to get all task for template
    """   
    def get_task(self, task_id):
        """
        Retrieve a workflow's tasks by id.
        """
        if not task_id:
            return {"error": "task ID is required." , "success": False}

        try:
            
            result = self.db_connection.select_one(table_name='`workflow_tasks`',
                                                   condition='id = %s AND is_deleted = %s',
                                                   bind_variables=(task_id, 0,))
            if not result:
                return {"data": None, "success": False}

            return {"data": result, "success": True}
        except Exception as e:
            General.write_event(f"Error creating workflow task: {str(e)}")
            return {"error": f"Error retrieving workflow tasks: {str(e)}", "success": True}
           
    """
    function update to workflow task data 
    """
    def update_task(self, task_id, workflow_id, name, task_type):
        if not task_id or not workflow_id or not name or not task_type :
            return {"error": "task ID is required.", "success": False}

        try:
            update_data = {
                "workflow_id": workflow_id,
                "name": name,
                "task_type": task_type,
            }
            is_update = self.db_connection.update(
                table_name="`workflow_tasks`",
                condition_column="id",
                condition_value=task_id,
                update_data=update_data
            )

            if is_update != 0:
                return {"error": "Failed to delete task.", "success" : False}

            return {"success": True, "message": "task deleted successfully."}
        except Exception as e:
            General.write_event(f"Error creating workflow task: {str(e)}")
            return {"error": f"Error while deleting  task: {str(e)}" ,"success" : False}
        
   
    """
    function delete to workflow task data 
    """
    def delete_task(self, task_id):
        if not task_id:
            return {"error": "task ID is required." , "success": False}

        try:
            is_update = self.db_connection.update(
                table_name="`workflow_tasks`",
                condition_column="id",
                condition_value=task_id,
                update_data={"is_deleted": True}
            )

            if is_update != 0:
                return {"error": "Failed to delete task.", "success" : False}

            return {"success": True, "message": "task deleted successfully."}
        except Exception as e:
            General.write_event(f"Error creating workflow task: {str(e)}")
            return {"error": f"Error while deleting  task: {str(e)}" ,"success" : False}

    """ Assign task to group. """
    # def assign_task_group(self, task_id, group_id, level_id=0):
    #     if not task_id or not group_id:
    #         return {"error": "Task or Group ID is required.",
    #                 "success": False}
    #
    #     try:
    #         data = {
    #             "task_id": task_id,
    #             "group_id": group_id,
    #             "level_id": level_id
    #         }
    #
    #         insert_task = self.db_connection.create("`task_groups`", data, debug=True)
    #         # print(task_id)
    #         if insert_task is None:
    #             General.write_event("Failed to assign task to group")
    #             return {"error": "Failed to assign task to group.", "success": False}
    #
    #         return {"task_id": task_id, "success": True}
    #     except Exception as e:
    #         General.write_event(f"Error assign task to group: {str(e)}")
    #         return {"error": f"Error assign task to group: {str(e)}", "success": False}

    def get_first_task_in_template(self, template_id):
        """
        Retrieve a first workflow task in specific template.
        """
        if not template_id:
            return {"error": "template ID is required.", "success": False}

        try:
            query = 'SELECT id FROM workflow_tasks WHERE template_id = %s ORDER BY id LIMIT 1;'
            result = self.db_connection.execute_raw(query=query,
                                                    bind_variables=(template_id,))
            if not result:
                return {"task_id": None, "success": False}

            return {"task_id": result, "success": True}
        except Exception as e:
            General.write_event(f"Error Retrieve workflow task for specific template: {str(e)}")
            return {"error": f"Error Retrieve workflow task for specific template: {str(e)}", "success": True}

    def get_task_info(self, task_id):
        """
        Retrieve a  workflow task info about group and level in specific template.
        """
        if not task_id:
            return {"error": "task ID is required.", "success": False}

        try:
            query = ('SELECT t.id,t.template_id,t.name,t.task_type,t.assigned_to,t.assigned_role,'
                     'tg.group_id,tg.level_id,g.group_name,l.name AS level_name  '
                     'FROM workflow_tasks t '
                     'LEFT JOIN task_groups tg ON tg.task_id = t.id '
                     'LEFT JOIN `groups` g ON g.group_id = tg.group_id '
                     'LEFT JOIN group_level l ON l.id = tg.level_id '
                     'WHERE t.id = %s ;')
            result = self.db_connection.execute_raw(query=query,
                                                    bind_variables=(task_id,))
            if not result:
                return {"data": None, "success": False}

            return {"data": result, "success": True}
        except Exception as e:
            General.write_event(f"Error Retrieve a workflow task info about group and level in "
                                f"specific template: {str(e)}")
            return {"error": f"Error Retrieve a workflow task info about group and level in "
                             f"specific template: {str(e)}", "success": True}