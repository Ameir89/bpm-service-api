from application.mysql_connection import Connection
from application.common.general import General
# from application.models.workflow.workflow import Workflows

class Templates:
    def __init__(self):
        self.db_connection = Connection()

    def create_workflow_template(self,workflow_id , diagram_json , status,created_by):
        """
        Create a new work and return the workflow ID.
        """
        if  not workflow_id or  not created_by:
            return {"error": "Workflow id or created_by are required." , "success":False}

        try:
            data = {
                "workflow_id":workflow_id,
                "diagram_json": diagram_json,
                "status": status,
                "created_by": created_by
            }

            template_id = self.db_connection.create("`workflow_templates`", data,debug=True)
            
            if not template_id:
                return {"error": "Failed to create workflow templets."}
            
            # workflow = Workflows()
            # assign_templet = workflow.assign_templet_to_workflow(workflow_id,templet_id)
            
            # if not assign_templet:
            #     General.write_event("Failed to create workflow templets.")
            #     return {"error": "Failed to create workflow templets." ,"success" : False}
                
            return {"templet_id": template_id, "success":True}
        except Exception as e:
            return {"error": f"Error creating workflow templet: {str(e)}"  , "success":False}
        
    
    """
    Function use to update templates
    """   
    def update_workflow_templates(self, tamplate_id, workflow_id, diagram_json , status):
        if not tamplate_id or not workflow_id or not diagram_json or not status :
            return {"error": "lable,  description or status is required."}

        try:
            data = {
                "workflow_id": workflow_id,
                "diagram_json": diagram_json,
                "status": status
            }
            is_update = self.db_connection.update(
                table_name="`workflow_templates`",
                condition_column="id",
                condition_value=tamplate_id,
                update_data=data
            )

            if is_update != 0:
                return {"error": "Failed to update workflow  data." , "success": False}

            return {"success": True, "message": "workflow data updated successfully."}
        except Exception as e:
            return {"error": f"Error while updating data for workflow: {str(e)}", "success": False}
        
  
    """
    Function use to get all templates by workflow id
    """   
    def get_workflow_template_by_wid(self, workflow_id):
        """
        Retrieve a workflow's templates by its workflow ID.
        """
        if not workflow_id:
            return {"error": "Workflow ID is required." , "success": False}

        try:
            base_query = """
                SELECT w.*, wt.* ,u.full_name
                FROM workflow_templates wt
                LEFT JOIN workflows w ON w.id = wt.workflow_id
                LEFT JOIN users u ON u.id = wt.created_by
                WHERE wt.workflow_id = %s AND wt.is_deleted = 0 AND wt.status = 1
                ORDER BY wt.id DESC 
                LIMIT 1
            """

            # if active:
            #     base_query += " AND wt.status = 0"

            result = self.db_connection.execute_raw(
                query=base_query,
                bind_variables=(workflow_id,),
                debug=False
            )
            

            if not result:
                return {"data": None, "success": False}

            return {"data": result[0], "success": True}
        except Exception as e:
            return {"error": f"Error retrieving workflows: {str(e)}" , "success" : True}
        
    """
    Function use to get all templates
    """   
    def get_workflow_templates(self):
        """
        Retrieve a workflow's templates.
        """
        try:
            base_query = """
                SELECT w.*, wt.* ,u.full_name
                FROM workflow_templates wt
                LEFT JOIN workflows w ON w.id = wt.workflow_id
                LEFT JOIN users u ON u.id = wt.created_by
                WHERE  wt.is_deleted = 0 
            """

            # if active:
            #     base_query += " AND wt.status = 0"

            result = self.db_connection.execute_raw(
                query=base_query,
                bind_variables= None,
                debug=True
            )

            if not result:
                return {"error": "templates not found.", "success": False}

            return {"data": result, "success": True}
        except Exception as e:
            return {"error": f"Error retrieving templates: {str(e)}" , "success" : True}
        
  

    """
    Function use to change workflows templets status
    """ 
    def change_workflow_template_status(self, template_id, status):
        if not template_id:
            return {"error": "templet ID is required.", "success": False}
        
        if status not in [0, 1]:
            return {"error": "Invalid status. Status must be 0 or 1." , "success": False}

        try:
            is_update = self.db_connection.update(
                table_name="`workflow_templates`",
                condition_column="id",
                condition_value=template_id,
                update_data={"status": status},
                debug=True
            )
            
            if is_update != 0:
                return {"error": "Failed to change workflow status.", "success": False}

            return {"success": True, "message": "Workflow status updated successfully."}
        except Exception as e:
            return {"error": f"Error while changing status for workflow: {str(e)}", "success": False}
    
    
   
    """
    function delete to workflow template data 
    """
    def delete_workflow_template(self, template_id):
        if not template_id:
            return {"error": "Workflow ID is required." , "success": False}

        try:
            is_update = self.db_connection.update(
                table_name="`workflow_templates`",
                condition_column="id",
                condition_value=template_id,
                update_data={"is_deleted": True}
            )

            if is_update != 0:
                return {"error": "Failed to delete template workflow.", "success" : False}

            return {"success": True, "message": "workflow template deleted successfully."}
        except Exception as e:
            return {"error": f"Error while deleting  workflow template: {str(e)}" ,"success" : False}

    """Function use to get all templates by workflow id """
    def get_workflow_template_by_id(self, template_id):
        """
        Retrieve a workflow's templates by its template ID.
        """
        if not template_id:
            return {"error": "template ID is required.", "success": False}

        try:
            base_query = """
                    SELECT w.*, wt.* ,u.full_name
                    FROM workflow_templates wt
                    LEFT JOIN workflows w ON w.id = wt.workflow_id
                    LEFT JOIN users u ON u.id = wt.created_by
                    WHERE wt.id = %s AND wt.is_deleted = 0 AND wt.status = 1      
                """
            result = self.db_connection.execute_raw(
                query=base_query,
                bind_variables=(template_id,),
                debug=False
            )

            if not result:
                return {"data": None, "success": False}

            return {"data": result[0], "success": True}
        except Exception as e:
            return {"error": f"Error retrieving workflow template: {str(e)}", "success": True}

    """
        Function use to change workflows templets status
        """

    def execute_workflow_template_done(self, template_id):
        if not template_id:
            return {"error": "templet ID is required.", "success": False}



        try:
            is_update = self.db_connection.update(
                table_name="`workflow_templates`",
                condition_column="id",
                condition_value=template_id,
                update_data={"execute": 1},
                debug=True
            )

            if is_update != 0:
                return {"error": "Failed to change workflow template executed to done.", "success": False}

            return {"success": True, "message": "execute workflow template done, successfully."}
        except Exception as e:
            return {"error": f"Error while changing status for workflow: {str(e)}", "success": False}