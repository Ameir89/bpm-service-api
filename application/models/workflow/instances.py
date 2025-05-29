from application.mysql_connection import Connection
from application.common.general import General


class Instances:
    def __init__(self):
        self.db_connection = Connection()

    def exists(self, request_id):
        if not request_id:
            return {"error": "request id is required.",
                    "success": False}

        try:
            data = self.db_connection.select_one(table_name='`workflow_instances`',
                                                 condition='request_id = %s',
                                                 bind_variables=(request_id,))
            if not data:
                return {"data": None, "success": True}

            return {"data ": data, "success": True}
        except Exception as e:
            General.write_event(f"Error Check for existing instance with same request_id: {str(e)}")
            return {"error": f"Error Check for existing instance with same request_id: {str(e)}", "success": False}


    """
        Create a new workflow instance.
    """

    def create_instance(self, template_id, request_id, status, started_at):
        if not template_id or not request_id or not status:
            return {"error": "Task template id , request id ,started at  are required.",
                    "success": False}

        try:
            data = {
                "template_id": template_id,
                "request_id": request_id,
                "status": status,
                "started_at": started_at
            }

            instance_id = self.db_connection.create("`workflow_instances`", data, debug=True)
            print(instance_id)
            if not instance_id:
                return {"error": "Failed to create workflow instance.", "success": False}

            return {"instance_id ": instance_id, "success": True}
        except Exception as e:
            General.write_event(f"Error creating workflow instances: {str(e)}")
            return {"error": f"Error creating workflow instances: {str(e)}", "success": False}

    """
    Function use to get all workflow instances for template
    """
    def get_instances_by_status(self, status="Running"):
        """
        Retrieve a workflow's instances by status.
        """
        if not status:
            return {"error": "status is required.", "success": False}

        try:

            result = self.db_connection.select(table_name='`workflow_instances`',
                                               condition='status = %s',
                                               bind_variables=(status,))
            if not result:
                return {"data": None, "success": False}

            return {"data": result, "success": True}
        except Exception as e:
            General.write_event(f"Error retrieving workflow instance by status: {str(e)}")
            return {"error": f"Error retrieving workflow instance by status: {str(e)}", "success": True}

    def update_instance_status(self, instance_id, status="Completed"):
        """ function update to workflow instance  """
        if not instance_id or not status:
            return {"error": "instance ID is required.", "success": False}

        try:
            update_data = {
                "instance_id": instance_id,
                "status": status,
            }
            is_update = self.db_connection.update(
                table_name="`workflow_instances`",
                condition_column="id",
                condition_value=instance_id,
                update_data=update_data
            )

            if is_update != 0:
                return {"error": "Failed to update instance status.", "success": False}

            return {"success": True, "message": "instance status updated successfully."}
        except Exception as e:
            General.write_event(f"Error update workflow instance: {str(e)}")
            return {"error": f"Error update workflow instance: {str(e)}", "success": False}

