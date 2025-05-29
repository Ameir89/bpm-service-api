from application.mysql_connection import Connection
from application.common.general import General


class FieldTypes:
    def __init__(self):
        self.db_connection = Connection()

    def create_field_type(self, name):
        """
        Create a new action type and return the ID.
        """
        if not name:
            return {"error": "filed type name  required."}

        try:
            data = {
                "name": name,
            }

            filed_type_id = self.db_connection.create("`filed_types`", data, debug=True)

            if not filed_type_id:
                return {"error": "Failed to create filed type."}

            return {"filed_type_id": filed_type_id}
        except Exception as e:
            return {"error": f"Error creating filed type: {str(e)}"}

    def get_field_type(self, field_type_id):
        """
        Retrieve filed type details by its ID.
        """
        if not field_type_id:
            return {"error": "filed type id is required."}

        try:
            result = self.db_connection.select_one(table_name="`filed_types`", condition="id = %s ",
                                                   bind_variables=(field_type_id,), debug=True)

            if not result:
                return {"error": "action type not found."}

            return result
        except Exception as e:
            return {"error": f"Error retrieving action type: {str(e)}"}

    """
    Function to get list of field types 
    """

    def list_field_types(self):
        """
        Retrieve all field types.
        """
        try:
            """ Zero means except soft deleted """
            results = self.db_connection.select(table_name="`filed_types`")

            if not results:
                return {"error": "No data for action types found."}

            return results
        except Exception as e:
            return {"error": f"Error listing field types: {str(e)}"}

    """
        Function to get list of field types enums
        """

    def list_field_types_enums(self):
        """
        Retrieve all field types enums.
        """
        try:
            sql = "select name from filed_types"
            results = self.db_connection.execute_raw(query=sql)

            if not results:
                return {"error": "No data for field types enums found."}

            return results
        except Exception as e:
            return {"error": f"Error listing field types enums: {str(e)}"}

    """
    function use to update field type data 
    """

    def update_field_type(self, field_type_id, name):
        if not name:
            return {"error": "field type  ID is required."}

        try:
            is_update = self.db_connection.update(
                table_name="`filed_types`",
                condition_column="id",
                condition_value=field_type_id,
                update_data={"name": name},
                debug=True
            )

            if is_update != 0:
                return {"error": "Failed to update action type data."}

            return {"success": True, "message": "action type data updated successfully."}
        except Exception as e:
            return {"error": f"Error while updating data for action type: {str(e)}"}
