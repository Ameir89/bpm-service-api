from application.mysql_connection import Connection 
from application.common.general import General

class Permissions:
    def __init__(self):
        self.db_connection = Connection()
        
    def create_permission(self, name, display_name=None, description=None):
        """
        Create a new role and associate it with permissions.

        Args:
            name (str): Name of the role (required).
            display_name (str): Human-readable name for the role (optional).
            description (str): Description of the role (optional).
           

        Returns:
            dict: A dictionary with `permission_id` if successful, or an error message if failed.
        """
        if not name:
            return {"error": "Permission name is required."}

        try:
            # Prepare permission data
            permission_data = {
                "name": name,
                "display_name": display_name,
                "description": description,
            }

            # Start a transaction (if supported)
            # self.db_connection.start_transaction()

            # Insert the permission into the database
            permission_id = self.db_connection.create("`roles`", permission_data)

            if not permission_id:
                # self.db_connection.rollback()  # Rollback in case of failure
                General.write_event("Failed to create the permission.")
                return {"error": "Failed to create the permission."}

            # Commit transaction if everything is successful
            # self.db_connection.commit()

            return {"permission_id": permission_id}

        except Exception as e:
            # self.db_connection.rollback()  # Ensure rollback on error
            General.write_event(f"Error creating permission: {str(e)}")
            return {"error": f"Error creating permission: {str(e)}"}


    
    def get_permission_by_id(self, permission_id):
        """
        Retrieve a permission's details by its ID, including associated permissions.
        """
        if not permission_id:
            return {"error": "Permission ID is required."}

        try:
            # Fetch permissions details
            permission = self.db_connection.select_one(
                table_name="permissions",  # Removed backticks (they are unnecessary in Python queries)
                condition="id = %s AND is_deleted = %s",
                bind_variables=(permission_id, 0)
            )

            if not permission:
                return {"error": "Permission not found."}

            return permission

        except Exception as e:
            error_message = f"Error retrieving role: {str(e)}"
            General.write_event(error_message)  # Log error for debugging
            return {"error": error_message}

        
    """
    Function to get list of user using paginations
    """         
    def list_permissions(self, page=1, page_size=10):
        """
        Retrieve user with pagination.
        :param page: The page number (1-based index).
        :param page_size: The number of items per page.
        """
        try:
            # Zero means except soft deleted
            offset = (page - 1) * page_size  # Calculate the offset

            # Add LIMIT and OFFSET for pagination
           
            # Query to fetch paginated user data with role, group, and level details
            query = (
                "SELECT * FROM permissions WHERE is_deleted = %s LIMIT %s OFFSET %s"
            )
            bind_variables = (0, page_size, offset)
            results = self.db_connection.execute_raw(query,bind_variables)
            if not results:
                return {"error": "No permissions found."}

            # Fetch total count of roles for pagination metadata
            total_count_condition = "is_deleted = %s"
            total_count_results = self.db_connection.select(
                table_name="`permissions`",
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
            return {"error": f"Error listing permissions: {str(e)}"}

  
    def delete_permission(self, permission_id):
        if not permission_id:
            return {"error": "Permission ID is required."}

        try:
            is_update = self.db_connection.update(
                table_name="`permissions`",
                condition_column="id",
                condition_value= permission_id,
                update_data={"is_deleted": True},
                debug=True
            )

            if is_update != 0:
                return {"error": "Failed to delete role."}

            return {"success": True, "message": "Permission deleted successfully."}
        except Exception as e:
            return {"error": f"Error while deleting Permission: {str(e)}"}
        
    def get_permission_by_role_id(self, role_id):
        """
        Retrieve a permission's details by role its ID, including associated permissions.
        """
        if not role_id:
            return {"error": "Role ID is required."}

        try:
            # Fetch permissions details
            query = """ 
                SELECT DISTINCT p.* 
                FROM permissions p
                INNER JOIN permission_role pr ON p.id = pr.permission_id
                WHERE pr.role_id = %s;
            """
            permissions = self.db_connection.execute_raw(query=query, bind_variables=(role_id,))

            if not permissions:
                return {"error": "Permission not found."}

            return permissions

        except Exception as e:
            error_message = f"Error retrieving role: {str(e)}"
            General.write_event(error_message)  # Log error for debugging
            return {"error": error_message}