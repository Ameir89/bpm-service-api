from application.mysql_connection import Connection 
from application.common.general import General

class Roles:
    def __init__(self):
        self.db_connection = Connection()
        
    def create_role(self, name, parent_role=None, display_name=None, description=None, permissions=None):
        """
        Create a new role and associate it with permissions, then return the role ID.

        Args:
            name (str): Name of the role (required).
            parent_role (int): ID of the parent role (optional).
            display_name (str): Human-readable name for the role (optional).
            description (str): Description of the role (optional).
            permissions (list): List of permission IDs to associate with the role (optional).

        Returns:
            dict: A dictionary with `role_id` if successful, or an error message if failed.
        """
        if not name:
            return {"error": "Role name is required."}

        if permissions and not isinstance(permissions, list):
            return {"error": "Permissions must be a list of integers."}

        try:
            # Prepare role data
            role_data = {
                "name": name,
                "parent_role": parent_role,
                "display_name": display_name,
                "description": description,
            }

            # Start a transaction (if supported)
            # self.db_connection.start_transaction()

            # Insert the role into the database
            role_id = self.db_connection.create("`roles`", role_data)

            if not role_id:
                # self.db_connection.rollback()  # Rollback in case of failure
                General.write_event("Failed to create the role.")
                return {"error": "Failed to create the role."}

            # Associate permissions with the role
            if permissions:
                try:
                    print(permissions)
                    # Ensure all permissions are valid integers
                    
                    permission_data = [{"permission_id": int(permission), "role_id": role_id} for permission in permissions]
                    print(permission_data)
                    # Bulk insert permissions into `permission_role` table
                    insert_count = self.db_connection.create_many("permission_role", permission_data)
                    

                    if insert_count != len(permission_data):
                        General.write_event("Some permissions failed to insert.")
                        raise Exception("Some permissions failed to insert.")

                except Exception as perm_error:
                    # self.db_connection.rollback()  # Rollback the transaction
                    General.write_event(f"Failed to associate permissions: {str(perm_error)}")
                    return {"error": f"Failed to associate permissions: {str(perm_error)}"}

            # Commit transaction if everything is successful
            # self.db_connection.commit()

            return {"role_id": role_id}

        except Exception as e:
            # self.db_connection.rollback()  # Ensure rollback on error
            General.write_event(f"Error creating role: {str(e)}")
            return {"error": f"Error creating role: {str(e)}"}

  
   
    
    def get_role_by_id(self, role_id):
        """
        Retrieve a role's details by its ID, including associated permissions.
        """
        if not role_id:
            return {"error": "Role ID is required."}

        try:
            # Fetch role details
            role = self.db_connection.select_one(
                table_name="roles",  # Removed backticks (they are unnecessary in Python queries)
                condition="id = %s AND is_deleted = %s",
                bind_variables=(role_id, 0)
            )

            if not role:
                return {"error": "Role not found."}

            # Fetch associated permissions
            query = """
                SELECT DISTINCT p.* 
                FROM permissions p
                INNER JOIN permission_role pr ON p.id = pr.permission_id
                WHERE pr.role_id = %s;
            """
            permissions = self.db_connection.execute_raw(query=query, bind_variables=(role_id,))

            # Add permissions to role details
            role["permissions"] = permissions if permissions else []

            return role

        except Exception as e:
            error_message = f"Error retrieving role: {str(e)}"
            General.write_event(error_message)  # Log error for debugging
            return {"error": error_message}

        
    """
    Function to get list of user using paginations
    """         
    def list_roles(self, page=1, page_size=10):
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
                "SELECT * FROM roles WHERE is_deleted = %s LIMIT %s OFFSET %s"
            )
            bind_variables = (0, page_size, offset)
            results = self.db_connection.execute_raw(query,bind_variables)
            if not results:
                return {"error": "No roles found."}

            # Fetch total count of roles for pagination metadata
            total_count_condition = "is_deleted = %s"
            total_count_results = self.db_connection.select(
                table_name="`roles`",
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
            return {"error": f"Error listing roles: {str(e)}"}

  
    def delete_role(self, role_id):
        if not role_id:
            return {"error": "Role ID is required."}

        try:
            is_update = self.db_connection.update(
                table_name="`roles`",
                condition_column="id",
                condition_value= role_id,
                update_data={"is_deleted": True}
            )

            if is_update != 0:
                return {"error": "Failed to delete role."}

            return {"success": True, "message": "Role deleted successfully."}
        except Exception as e:
            return {"error": f"Error while deleting role: {str(e)}"}
        
