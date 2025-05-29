from application.mysql_connection import Connection
from application.common.general import General


class ActionTypes:
    def __init__(self):
        self.db_connection = Connection()

    def create_action_type(self, name, color):
        """
        Create a new action type and return the ID.
        """
        if not name:
            return {"error": "action type name  required."}

        try:
            data = {
                "name": name,
                "color": color,
            }

            action_type_id = self.db_connection.create("`action_types`", data, debug=True)

            if not action_type_id:
                return {"error": "Failed to create action type."}

            return {"action_type_id": action_type_id}
        except Exception as e:
            return {"error": f"Error creating action type: {str(e)}"}

    def get_action_type(self, action_type_id):
        """
        Retrieve a action type details by its ID.
        """
        if not action_type_id:
            return {"error": "action type id is required."}

        try:
            result = self.db_connection.select_one(table_name="`action_types`", condition="id = %s ",
                                                   bind_variables=(action_type_id,), debug=True)

            if not result:
                return {"error": "action type not found."}

            return result
        except Exception as e:
            return {"error": f"Error retrieving action type: {str(e)}"}

    """
    Function to get list of action types 
    """

    def list_action_types(self):
        """
        Retrieve all action types.
        """
        try:
            """ Zero means except soft deleted """
            results = self.db_connection.select(table_name="`action_types`")

            if not results:
                return {"error": "No data for action types found."}

            return results
        except Exception as e:
            return {"error": f"Error listing action types: {str(e)}"}

    """
        Function to get list of action types enums
        """

    def list_action_types_enums(self):
        """
        Retrieve all action types enums.
        """
        try:
            sql = "select name from action_types"
            results = self.db_connection.execute_raw(query=sql)

            if not results:
                return {"error": "No data for action types enums found."}

            return results
        except Exception as e:
            return {"error": f"Error listing action types enums: {str(e)}"}

    """
    function use to update action type data 
    """

    def update_action_type(self,action_type_id, name, color):
        if not name:
            return {"error": "action type  ID is required."}

        try:
            is_update = self.db_connection.update(
                table_name="`action_types`",
                condition_column="id",
                condition_value=action_type_id,
                update_data={"name": name, "color": color},
                debug=True
            )

            if is_update != 0:
                return {"error": "Failed to update action type data."}

            return {"success": True, "message": "action type data updated successfully."}
        except Exception as e:
            return {"error": f"Error while updating data for action type: {str(e)}"}
