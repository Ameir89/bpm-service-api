from application.mysql_connection import Connection 
from application.common.general import General

class Groups:
    def __init__(self):
        self.db_connection = Connection()

    def create_group(self, group_name, description, status, created_by):
        """
        Create a new group and return the group ID.
        """
        if not group_name or not created_by:
            return {"error": "Group name and created_by are required."}

        try:
            data = {
                "group_name": group_name,
                "description": description,
                "status": status,
                "created_by": created_by
            }

            group_id = self.db_connection.create("`groups`", data,debug=True)
            
            if not group_id:
                return {"error": "Failed to create group."}

            return {"group_id": group_id}
        except Exception as e:
            return {"error": f"Error creating group: {str(e)}"}

    def assign_group_to_activity(self, task_id, group_id):
        """
        Assign a group to an activity.
        """
        if not task_id or not group_id:
            return {"error": "Activity ID and group ID are required."}

        try:
            data = {
                "task_id": task_id,
                "group_id": group_id
            }

            result_id = self.db_connection.create("task_group", data)
            if not result_id:
                return {"error": "Failed to assign group to task."}

            return {"assignment_id": result_id}
        except Exception as e:
            return {"error": f"Error assigning group to task: {str(e)}"}
        

    def get_group(self, group_id):
        """
        Retrieve a group's details by its ID.
        """
        if not group_id:
            return {"error": "Group ID is required."}

        try:
            # result = select_one("users", columns=["name", "email"], condition="id = %s", bind_variables=(1,), debug=True)
            result = self.db_connection.select_one(table_name="`groups`",condition="group_id = %s ", bind_variables=(group_id,),debug=True)

            if not result:
                return {"error": "Group not found."}

            return result
        except Exception as e:
            return {"error": f"Error retrieving group: {str(e)}"}
        
    def get_group_name(self, group_name):
        """
        Retrieve a group's details by its group_name, using partial matching with 'LIKE'.
        """
        if not group_name:
            return {"error": "Group name is required."}

        try:
            # Use the '%' wildcard for partial matching with the LIKE operator
            like_pattern = f"%{group_name}%"
            result = self.db_connection.select(
                table_name="`groups`",
                condition="group_name LIKE %s",
                bind_variables=(like_pattern,),
                debug=True
            )

            if not result:
                return {"error": "Group not found."}

            return result
        except Exception as e:
            return {"error": f"Error retrieving group: {str(e)}"}
            
    """
    Function to get list of Group using paginations
    """         
    def list_groups(self, page=1, page_size=10):
        """
        Retrieve groups with pagination.
        :param page: The page number (1-based index).
        :param page_size: The number of items per page.
        """
        try:
            # Zero means except soft deleted
            offset = (page - 1) * page_size  # Calculate the offset

            # Add LIMIT and OFFSET for pagination
            condition = "is_deleted = %s LIMIT %s OFFSET %s"
            bind_variables = (0, page_size, offset)

            results = self.db_connection.select(
                table_name="`groups`",
                condition=condition,
                bind_variables=bind_variables,
                debug=True
            )

            if not results:
                return {"error": "No groups found."}

            # Fetch total count of groups for pagination metadata
            total_count_condition = "is_deleted = %s"
            total_count_results = self.db_connection.select(
                table_name="`groups`",
                columns=["COUNT(*) as total"],
                condition=total_count_condition,
                bind_variables=(0,)
            )
            total_count = total_count_results[0]["total"] if total_count_results else 0

            # Prepare response with pagination metadata
            return {
                "data": results,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_items": total_count,
                    "total_pages": (total_count + page_size - 1) // page_size
                }
            }
        except Exception as e:
            return {"error": f"Error listing groups: {str(e)}"}
  
    """
    Function use to change group status
    """ 
    def change_group_status(self, group_id, status):
        if not group_id:
            return {"error": "Group ID is required."}
        
        if status not in [0, 1]:
            return {"error": "Invalid status. Status must be 0 or 1."}

        try:
            is_update = self.db_connection.update(
                table_name="`groups`",
                condition_column="group_id",
                condition_value=group_id,
                update_data={"status": status},
                debug=True
            )
            
            if is_update != 0:
                return {"error": "Failed to change group status."}

            return {"success": True, "message": "Group status updated successfully."}
        except Exception as e:
            return {"error": f"Error while changing status for group: {str(e)}"}

    """
    function use to update group data 
    """
    def update_group_data(self, group_id, group_name, description, status):
        if not group_id:
            return {"error": "Group ID is required."}

        try:
            is_update = self.db_connection.update(
                table_name="`groups`",
                condition_column="group_id",
                condition_value=group_id,
                update_data={"group_name": group_name, "description": description, "status": status}
            )

            if is_update != 0:
                return {"error": "Failed to update group data."}

            return {"success": True, "message": "Group data updated successfully."}
        except Exception as e:
            return {"error": f"Error while updating data for group: {str(e)}"}


    def delete_group(self, group_id):
        if not group_id:
            return {"error": "Group ID is required."}

        try:
            is_update = self.db_connection.update(
                table_name="`groups`",
                condition_column="group_id",
                condition_value=group_id,
                update_data={"is_deleted": True}
            )

            if is_update != 0:
                return {"error": "Failed to delete group."}

            return {"success": True, "message": "Group deleted successfully."}
        except Exception as e:
            return {"error": f"Error while deleting group: {str(e)}"}

