from application.mysql_connection import Connection 
from application.common.general import General

class Users:
    def __init__(self):
        self.db_connection = Connection()
        
    def get_user_by_username(self,username):
        if not username:
            General.write_event("Error username is required.")
            return {"error": "username is required." ,"success": False}
        try:
            user = self.db_connection.select_one(table_name='`users`',
                                                     condition="username = %s" ,
                                                     bind_variables=(username,) )
            if user:
                return True
            return False
        except Exception as e:
            General.write_event(f"Error featch usre info : {str(e)}")
            return {"error": f"Error featch usre info : {str(e)}" ,"success": False}
        
    def get_user_by_username_for_login(self, username): 
        try:
            # Query to fetch paginated user data with role, group, and level details
            query = (
                "SELECT u.*, r.name as role_name, g.group_name, l.name as level_name "
                "FROM users u "
                "LEFT JOIN `groups` g ON g.group_id = u.group "
                "LEFT JOIN roles r ON r.id = u.role "
                "LEFT JOIN group_level l ON l.id = u.level "
                "WHERE u.username = %s and u.status = %s and u.is_deleted = %s "
            )
            bind_variables = (username, 1, 0)
            results = self.db_connection.execute_raw(query,bind_variables)
            if not results:
                return {"error": "No users found.","success": False}

            # Prepare response with pagination metadata
            return {"data": results[0] , "success": True}
        except Exception as e:
            return {"error": f"Error listing users: {str(e)}" ,"success": False}
        
        
    def create_user(self, username,full_name, password,group,level,role,status,created_by):
        """
        Create a new users and return the group ID.
        """
        if not username or not full_name or not password or not group or not level or not role:
            return {"error": "user data are required."}

        try:
            data = {
                "full_name": full_name,
                "username": username,
                "password": password,
                "`group`": group,
                "level": level,
                "role": role,
                "status": status,
                "created_by": created_by
            }

            user_id = self.db_connection.create("`users`", data)
            
            if not user_id:
                return {"error": "Failed to create user." ,"success": False}

            return {"user_id": user_id}
        except Exception as e:
            return {"error": f"Error creating user: {str(e)}" ,"success": False}

    
    def get_user_by_id(self, user_id):
        """
        Retrieve a user's details by its ID.
        """
        if not user_id:
            return {"error": "User ID is required." ,"success": False}

        try:
            query = """
                SELECT 
                    u.id, 
                    u.full_name, 
                    u.username, 
                    u.status, 
                    u.creation_date, 
                    u.role AS role_id, 
                    r.name AS role_name, 
                    u.`group` AS group_id, 
                    g.group_name, 
                    u.`level` AS level_id, 
                    l.name AS level_name 
                FROM users u 
                LEFT JOIN `groups` g ON g.group_id = u.`group` 
                LEFT JOIN roles r ON r.id = u.role 
                LEFT JOIN group_level l ON l.id = u.`level` 
                WHERE u.id = %s AND u.is_deleted = %s
            """
            bind_variables = (user_id, 0)
            result = self.db_connection.execute_raw(query,bind_variables)
            
            # result = self.db_connection.select_one(table_name="`users`", columns=("id","username","full_name","role","`group`","level","status","creation_date"),condition="id = %s AND is_deleted = %s", bind_variables=(user_id, 0))

            if not result:
                return {"error": "User not found." ,"success": False}

            return result[0]
        except Exception as e:
            return {"error": f"Error retrieving user: {str(e)}" ,"success": False}
        
    """
    Function to get list of user using paginations
    """         
    def list_users(self, page=1, page_size=10):
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
                "SELECT u.id,u.full_name,u.username,u.status,u.creation_date,u.role as role_id,r.name as role_name, "
                "u.`group` as group_id,g.group_name,u.`level` as level_id, l.name as level_name "
                "FROM dynamic_workflows_db.users u "
                "LEFT JOIN `groups` g ON g.group_id = u.`group` "
                "LEFT JOIN roles r ON r.id = u.role "
                "LEFT JOIN group_level l ON l.id = u.`level` "
                "WHERE u.is_deleted = %s "
                "LIMIT %s OFFSET %s"
            )
            bind_variables = (0, page_size, offset)
            results = self.db_connection.execute_raw(query,bind_variables)
            if not results:
                return {"error": "No users found." ,"success": False}

            # Fetch total count of users for pagination metadata
            total_count_condition = "is_deleted = %s"
            total_count_results = self.db_connection.select(
                table_name="`users`",
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
            return {"error": f"Error listing users: {str(e)}" ,"success": False}

    
    """
    function use to update user data 
    """
    def update_user_data(self, user_id,full_name, username, group,level,role ,status,password=None):
        if not user_id:
            return {"error": "User ID is required." ,"success": False}

        try:
            if not password:
                update_data = {"full_name":full_name ,"username": username, "`group`": group, 
                             "level": level, "role": role, "status": status}
            else:
                update_data = {"full_name":full_name ,"username": username, "password":password,
                               "`group`": group, "level": level, "role": role, "status": status}
                
            is_update = self.db_connection.update(
                table_name="`users`",
                condition_column="id",
                condition_value=user_id,
                update_data=update_data
            )

            if is_update != 0:
                return {"error": "Failed to update user data." ,"success": False}

            return {"success": True, "message": "User data updated successfully."}
        except Exception as e:
            return {"error": f"Error while updating data for user: {str(e)}" ,"success": False}


    def delete_user(self, user_id):
        if not user_id:
            return {"error": "User ID is required." ,"success": False}

        try:
            is_update = self.db_connection.update(
                table_name="`users`",
                condition_column="id",
                condition_value= user_id,
                update_data={"is_deleted": True}
            )

            if is_update != 0:
                return {"error": "Failed to delete user." ,"success": False}

            return {"success": True, "message": "User deleted successfully."}
        except Exception as e:
            return {"error": f"Error while deleting user: {str(e)}" ,"success": False}
        

    def update_user_password(user_id, new_password):
        """
        Change the password for a user.
        """
        if not user_id:
            return {"error": "User ID is required." ,"success": False}

        if not new_password:
            return {"error": "New password is required." ,"success": False}

        try:
            db_connection = Connection()
            is_update = db_connection.update(
                table_name="`users`",
                condition_column="id",
                condition_value=user_id,
                update_data={"password": new_password}
            )

            if is_update != 0:
                return {"error": "Failed to update the user password." ,"success": False}

            return {"success": True, "message": "Password updated successfully." }

        except Exception as e:
            General.write_event(f"Error in change_user_password: {e}")
            return {"error": f"Error while updating password: {str(e)}" ,"success": False}
     
     
    def search_user_name(self, search_value):
        """
        Retrieve a user's details by its name or full name, using partial matching with 'LIKE'.
        """
        if not search_value:
            return {"error": "User name or full name is required." ,"success": False}

        try:
            # Use the '%' wildcard for partial matching with the LIKE operator
            like_pattern = f"%{search_value}%"
            # result = self.db_connection.select(
            #     table_name="`users`",
            #     columns= ("id","username","full_name","role","`group`","level","status","creation_date","is_deleted"),
            #     condition="is_deleted = %s AND (username LIKE %s OR full_name LIKE %s)",
            #     bind_variables=(0, like_pattern, like_pattern),
            #     debug=True
            # )
            
            query = (
                "SELECT u.id,u.full_name,u.username,u.status,u.creation_date,u.role as role_id,r.name as role_name, "
                "u.`group` as group_id,g.group_name,u.`level` as level_id, l.name as level_name "
                "FROM dynamic_workflows_db.users u "
                "LEFT JOIN `groups` g ON g.group_id = u.`group` "
                "LEFT JOIN roles r ON r.id = u.role "
                "LEFT JOIN group_level l ON l.id = u.`level` "
                "WHERE u.is_deleted = %s AND (u.username LIKE %s OR u.full_name LIKE %s) "
            )
            bind_variables=(0, like_pattern, like_pattern)
            result = self.db_connection.execute_raw(query,bind_variables)

            if not result:
                return {"error": "User not found." ,"success": False}
            
            return result
        except Exception as e:
            return {"error": f"Error retrieving user: {str(e)}" ,"success": False}   
    