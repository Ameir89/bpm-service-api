from application.mysql_connection import Connection
from application.common.general import General
# from application.models.workflow.templates import Templates


class Services:
    def __init__(self):
        self.db_connection = Connection()

    def create_service(self, name, description, order, workflow_id):
        """
        Create a new work and return the workflow ID.
        """
        if not name or not workflow_id:
            return {"error": "service name and workflow_id are required.", "success": False}

        try:
            data = {
                "name": name,
                "description": description,
                "order": order,
                "workflow_id": workflow_id
            }

            service_id = self.db_connection.create("`services`", data, debug=True)

            if not service_id:
                return {"error": "Failed to create service."}

            return {"service_id": service_id, "success": True}
        except Exception as e:
            return {"error": f"Error creating service: {str(e)}", "success": False}

    def assign_templet_to_workflow(self, workflow_id, templet_id):
        """
        Assign a workflow to an templet .
        """
        if not workflow_id or not templet_id:
            return {"error": "workflow ID and templet ID are required.", "success": False}

        try:
            data = {
                "workflow_id": workflow_id,
                "template_id": templet_id,
            }

            result_id = self.db_connection.create("workflow_join_wt", data)
            if not result_id:
                return {"error": "Failed to assign workflow to templet.", "success": False}

            return {"assignment": True, "success": True}
        except Exception as e:
            return {"error": f"Error assigning workflow to templet: {str(e)}", "success": False}

    def get_workflow(self, workflow_id):
        """
        Retrieve a workflow's details by its ID.
        """
        if not workflow_id:
            return {"error": "Workflow ID is required."}

        try:
            query = """
                SELECT w.*, wt.id as template_id
                FROM dynamic_workflows_db.workflows w 
                LEFT JOIN workflow_templates wt ON wt.workflow_id = w.id 
                WHERE w.id = %s AND
                    (wt.is_deleted = %s AND wt.status = %s) 
                    OR 
                    (wt.workflow_id IS NULL AND w.is_deleted = %s ) 
            """

            bind_variables = (workflow_id, 0, 1, 0,)
            result = self.db_connection.execute_raw(query, bind_variables)

            # result = self.db_connection.select_one(table_name="`workflows`",condition="id = %s ", bind_variables=(workflow_id,),debug=True)

            if not result:
                return {"error": "Workflow not found.", "success": False}

            return {"data": result, "success": True}
        except Exception as e:
            return {"error": f"Error retrieving workflows: {str(e)}", "success": True}

    """
    Function to get list of Workflow using paginations
    """

    def list_workflows(self, page=1, page_size=10):
        """
        Retrieve workflows with pagination.
        :param page: The page number (1-based index).
        :param page_size: The number of items per page.
        """
        try:
            # حساب الإزاحة (offset)
            offset = (page - 1) * page_size

            # استعلام جلب البيانات مع التحقق من الحذف والحالة
            query = """
                SELECT w.*, wt.id as template_id
                FROM dynamic_workflows_db.workflows w 
                LEFT JOIN workflow_templates wt ON wt.workflow_id = w.id 
                WHERE 
                    (wt.is_deleted = %s AND wt.status = %s) 
                    OR 
                    (wt.workflow_id IS NULL AND w.is_deleted = %s ) 
                LIMIT %s OFFSET %s
            """

            bind_variables = (0, 1, 0, page_size, offset)
            results = self.db_connection.execute_raw(query, bind_variables)

            if not results:
                return {"error": "No workflows found.", "success": True}

            # استعلام لحساب العدد الإجمالي للسجلات
            count_query = """
                SELECT COUNT(*) AS total 
                FROM dynamic_workflows_db.workflows w 
                LEFT JOIN workflow_templates wt ON wt.workflow_id = w.id 
                WHERE 
                    (wt.is_deleted = %s AND wt.status = %s) 
                    OR 
                    (wt.workflow_id IS NULL AND w.is_deleted = %s)
            """

            count_variables = (0, 1, 0)
            total_count_results = self.db_connection.execute_raw(count_query, count_variables)

            # جلب العدد الإجمالي
            total_count = total_count_results[0]["total"] if total_count_results else 0

            # تحضير الاستجابة مع بيانات الصفحة
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
            return {"error": f"Error listing workflows: {str(e)}", "success": False}

        """
        Retrieve groups with pagination.
        :param page: The page number (1-based index).
        :param page_size: The number of items per page.
        """
        try:
            # Zero means except soft deleted
            offset = (page - 1) * page_size  # Calculate the offset
            qurey = """
                       SELECT w.*, wt.id FROM dynamic_workflows_db.workflows w 
                       left join workflow_templates wt on wt.workflow_id = w.id 
                       WHERE (wt.is_deleted = %s AND wt.status = %s) 
                       OR (wt.workflow_id IS NULL AND w.is_deleted = %s AND w.status = %s) 
                       LIMIT %s OFFSET %s
                       """
            # Add LIMIT and OFFSET for pagination
            # condition = "is_deleted = %s LIMIT %s OFFSET %s"
            bind_variables = (0, 1, 0, 1, page_size, offset)
            results = self.db_connection.execute_raw(qurey, bind_variables)
            # results = self.db_connection.select(
            #     table_name="`workflows`",
            #     condition=condition,
            #     bind_variables=bind_variables,
            #     debug=True
            # )

            if not results:
                return {"error": "No workflows found.", "success": True}

            # Fetch total count of groups for pagination metadata
            total_count_condition = "is_deleted = %s"
            sql = """
                       SELECT COUNT(w.*) as total workflows w 
                       left join workflow_templates wt on wt.workflow_id = w.id 
                       WHERE (wt.is_deleted = %s ) 
                       OR (wt.workflow_id IS NULL AND w.is_deleted = %s AND w.status = %s) 
                       """
            total_count_results = self.db_connection.execute_raw(qurey, (0, 0, 1))
            # total_count_results = self.db_connection.select(
            #     table_name="`workflows`",
            #     columns=["COUNT(*) as total"],
            #     condition=total_count_condition,
            #     bind_variables=(0,)
            # )
            total_count = total_count_results[0]["total"] if total_count_results else 0

            # Prepare response with pagination metadata
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
            return {"error": f"Error listing groups: {str(e)}", "success": False}

    """
    Function use to change workflows status
    """

    def change_workflow_status(self, workflow_id, status):
        if not workflow_id:
            return {"error": "Workflow ID is required.", "success": False}

        if status not in [0, 1]:
            return {"error": "Invalid status. Status must be 0 or 1.", "success": False}

        try:
            is_update = self.db_connection.update(
                table_name="`workflows`",
                condition_column="id",
                condition_value=workflow_id,
                update_data={"status": status},
                debug=True
            )

            if is_update != 0:
                return {"error": "Failed to change workflow status.", "success": False}

            return {"success": True, "message": "Workflow status updated successfully."}
        except Exception as e:
            return {"error": f"Error while changing status for workflow: {str(e)}", "success": False}

    """
    Function use to change workflows join templet status
    """

    def change_workflow_wt_status(self, workflow_id, templet_id, status):
        if not workflow_id:
            return {"error": "Workflow ID or Templet Id is required.", "success": False}

        if status not in [0, 1]:
            return {"error": "Invalid status. Status must be 0 or 1.", "success": False}

        try:
            is_update = self.db_connection.update(
                table_name="`workflows`",
                condition_column="workflow_id, templet_id",
                condition_value=(workflow_id, templet_id),
                update_data={"status": status},
                debug=True
            )

            if is_update != 0:
                return {"error": "Failed to change workflow status.", "success": False}

            return {"success": True, "message": "Workflow status updated successfully."}
        except Exception as e:
            return {"error": f"Error while changing status for workflow: {str(e)}", "success": False}

    """
    function update to workflow data 
    """

    def update_workflow_data(self, label, name, description, status, workflow_id):
        if not label or not name or not description:
            return {"error": "lable , name , description or status is required."}

        try:
            is_update = self.db_connection.update(
                table_name="`workflows`",
                condition_column="id",
                condition_value=workflow_id,
                update_data={"label": label, "name": name, "description": description, "status": status}
            )

            if is_update != 0:
                return {"error": "Failed to update workflow  data.", "success": False}

            return {"success": True, "message": "workflow data updated successfully."}
        except Exception as e:
            return {"error": f"Error while updating data for workflow: {str(e)}", "success": False}

    """
    function delete to workflow data 
    """

    def delete_workflow(self, workflow_id):
        if not workflow_id:
            return {"error": "Workflow ID is required.", "success": False}

        try:
            is_update = self.db_connection.update(
                table_name="`workflows`",
                condition_column="id",
                condition_value=workflow_id,
                update_data={"is_deleted": True}
            )

            if is_update != 0:
                return {"error": "Failed to delete workflow.", "success": False}

            return {"success": True, "message": "workflow deleted successfully."}
        except Exception as e:
            return {"error": f"Error while deleting workflow: {str(e)}", "success": False}