from application.mysql_connection import Connection 
from application.common.general import General

class Levels:
    def __init__(self):
        self.db_connection = Connection()

    def create_level(self, name, ar_name):
        """
        Create a new group and return the group ID.
        """
        if not name :
            return {"error": "level name  required."}

        try:
            data = {
                "name": name,
                "ar_name": ar_name,   
            }

            level_id = self.db_connection.create("`group_level`", data,debug=True)
            
            if not level_id:
                return {"error": "Failed to create level."}

            return {"level_id": level_id}
        except Exception as e:
            return {"error": f"Error creating level: {str(e)}"}

   
    def get_level(self, level_id):
        """
        Retrieve a group level details by its ID.
        """
        if not level_id:
            return {"error": "level ID is required."}

        try:
            # result = select_one("users", columns=["name", "email"], condition="id = %s", bind_variables=(1,), debug=True)
            result = self.db_connection.select_one(table_name="`group_level`",condition="id = %s ", bind_variables=(level_id,),debug=True)

            if not result:
                return {"error": "Group not found."}

            return result
        except Exception as e:
            return {"error": f"Error retrieving group: {str(e)}"}
        
 
    """
    Function to get list of Group using paginations
    """         
    def list_group_levels(self):
        """
        Retrieve all groups.
        """
        try:
            """ Zero means except soft deleted """
            results = self.db_connection.select(table_name="`group_level`",condition="is_deleted = %s ", bind_variables=(0,))

            if not results:
                return {"error": "No grouplevel found."}

            return results
        except Exception as e:
            return {"error": f"Error listing groups: {str(e)}"}
       
   
    """
    function use to update group data 
    """
    def update_group_level_data(self, level_id, name, ar_name):
        if not level_id:
            return {"error": "Group Level ID is required."}

        try:
            is_update = self.db_connection.update(
                table_name="`group_level`",
                condition_column="id",
                condition_value=level_id,
                update_data={"name": name, "ar_name": ar_name},
                debug=True
            )

            if is_update != 0:
                return {"error": "Failed to update group level data."}

            return {"success": True, "message": "Group level data updated successfully."}
        except Exception as e:
            return {"error": f"Error while updating data for group level: {str(e)}"}


    def delete_group_level(self, level_id):
        if not level_id:
            return {"error": "Group Level ID is required."}

        try:
            is_update = self.db_connection.update(
                table_name="`group_level`",
                condition_column="id",
                condition_value=level_id,
                update_data={"is_deleted": True},
                debug=True
            )

            if is_update != 0:
                return {"error": "Failed to delete group level."}

            return {"success": True, "message": "Group level deleted successfully."}
        except Exception as e:
            return {"error": f"Error while deleting group level: {str(e)}"}

