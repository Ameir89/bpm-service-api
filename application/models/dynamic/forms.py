from application.mysql_connection import Connection
from application.common.general import General
import json


class Forms:
    def __init__(self):
        pass

    @staticmethod
    def create_metadata(task_id, form_name, description):
        """
        Insert form metadata into the database and return the new form ID.

        Args:
            task_id (int): The ID of the task this form is associated with.
            form_name (str): The display name of the form.
            description (str): An optional form description.

        Returns:
            int: Newly created form ID.
            or
            dict: Error object if failure occurs.
        """
        try:
            db_connection = Connection()
            db = db_connection._connect()
            cursor = db.cursor()

            # Create a safe table name
            table_name = f"ts_{form_name.strip().lower().replace(' ', '_')}"
            if not table_name.isidentifier():
                raise ValueError("Invalid form name for table creation.")

            # Insert metadata
            cursor.execute(
                '''
                INSERT INTO forms (task_id, form_name, table_name, description)
                VALUES (%s, %s, %s, %s)
                ''',
                (task_id, form_name, table_name, description)
            )

            form_id = cursor.lastrowid

            db.commit()
            cursor.close()
            db.close()
            return form_id

        except Exception as e:
            General.write_event(f"Database error in create_metadata: {e}")
            return {"error": str(e)}

    # @staticmethod
    # def create_metadata(task_id, form_name, description):
    #     try:
    #         db_connection = Connection()
    #         db = db_connection._connect()
    #         cursor = db.cursor()
    #         table_name = f"ts_{form_name.lower().replace(' ', '_')}"
    #         # Insert form metadata
    #         cursor.execute(
    #             'INSERT INTO forms (task_id,form_name,table_name ,description ) VALUES (%s, %s, %s, %s)',
    #             (task_id, form_name, table_name, description)
    #         )
    #         form_id = cursor.lastrowid  # Get the inserted form ID
    #
    #         # Commit and close DB connection
    #         db.commit()
    #         cursor.close()
    #         db.close()
    #         return form_id
    #     except Exception as e:
    #         return {"error": str(e)}

    @staticmethod
    def create_form_fields(form_id, fields):
        try:
            db_connection = Connection()
            db = db_connection._connect()
            cursor = db.cursor()

            # Insert form fields
            for field in fields:
                label = field['label']
                name = field['name']
                placeholder = field['placeholder']
                field_type = field['field_type']
                options = json.dumps(field.get('options', None))  # Convert options to JSON if available
                # description = field['description']
                required = field['required']
                enabled = field['enabled']
                cursor.execute(
                    'INSERT INTO form_fields (form_id, label, name, placeholder, field_type, '
                    'options, required, enabled) '
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                    (form_id, label, name, placeholder, field_type, options, required, enabled)
                )

            # Commit and close DB connection
            db.commit()
            cursor.close()
            db.close()
            return True
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def create_form_field(form_id, field):
        try:
            db_connection = Connection()
            db = db_connection._connect()
            cursor = db.cursor()

            # Extract single field values
            label = field['label']
            name = field['name']
            placeholder = field.get('placeholder', '')
            field_type = field['field_type']  # fix: match the key used in your request JSON
            options = json.dumps(field.get('options'))  # optional
            required = int(field['required'])
            enabled = int(field['enabled'])

            cursor.execute(
                '''INSERT INTO form_fields 
                   (form_id, label, name, placeholder, field_type, options, required, enabled) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
                (form_id, label, name, placeholder, field_type, options, required, enabled)
            )

            db.commit()
            cursor.close()
            db.close()
            return {"form_id": form_id, "name": name}

        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def update_form_field(form_id, field_id, field):
        """
        Update an existing form field.

        Parameters:
            form_id (int): ID of the form the field belongs to.
            field_id (int): ID of the field to update.
            field (dict): Dictionary containing updated field values.

        Returns:
            dict: Success message or error message.
        """
        try:
            db_connection = Connection()
            db = db_connection._connect()
            cursor = db.cursor()

            # Extract field values with defaults
            label = field['label']
            name = field['name']
            placeholder = field.get('placeholder', '')
            field_type = field['field_type']
            options = json.dumps(field.get('options'))  # optional JSON field
            required = int(field['required'])
            enabled = int(field['enabled'])

            # Update the field in the database
            cursor.execute(
                '''UPDATE form_fields 
                   SET label = %s,
                       name = %s,
                       placeholder = %s,
                       field_type = %s,
                       options = %s,
                       required = %s,
                       enabled = %s
                   WHERE field_id = %s AND form_id = %s''',
                (label, name, placeholder, field_type, options, required, enabled, field_id, form_id)
            )

            # Commit changes and close connection
            db.commit()
            cursor.close()
            db.close()

            return {"form_id": form_id, "field_id": field_id, "updated": True}

        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def delete_form_field(form_id, field_id):
        try:
            db_connection = Connection()
            db = db_connection._connect()
            cursor = db.cursor()

            # Check if the field exists first (optional but recommended)
            cursor.execute(
                "SELECT id FROM form_fields WHERE id = %s AND form_id = %s",
                (field_id, form_id)
            )
            field = cursor.fetchone()

            if not field:
                return {"error": "Field not found"}

            # Delete the field
            cursor.execute(
                "DELETE FROM form_fields WHERE id = %s AND form_id = %s",
                (field_id, form_id)
            )

            db.commit()
            cursor.close()
            db.close()

            return True

        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def create_dynamic_table(form_name, fields):
        try:
            db_connection = Connection()
            db = db_connection._connect()
            cursor = db.cursor()

            # Create table based on form name
            table_name = f"ts_{form_name.lower().replace(' ', '_')}"
            columns = ["id INT PRIMARY KEY AUTO_INCREMENT"]

            # Generate columns based on fields
            for field in fields:
                name = field['name'].replace(' ', '_').lower()
                field_type = field['type']

                if field_type == 'text':
                    columns.append(f"{name} VARCHAR(255)")
                elif field_type == 'number':
                    columns.append(f"{name} INT")
                elif field_type == 'date':
                    columns.append(f"{name} DATE")
                elif field_type in ['dropdown', 'multi_select']:
                    columns.append(f"{name} JSON")  # Store options as JSON
                elif field_type == 'file':
                    columns.append(f"{name} TEXT")  # Store file paths or metadata
                else:
                    columns.append(f"{name} TEXT")  # Default fallback

            # Build and execute the CREATE TABLE query
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)});"
            cursor.execute(query)

            # Commit and close DB connection
            db.commit()
            cursor.close()
            db.close()
            return table_name
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def create_form_with_fields(task_id, form_name, description, fields):
        try:
            # Create form metadata
            form_id = Forms.create_metadata(task_id, form_name, description)
            if isinstance(form_id, dict):  # Check if error occurred
                return form_id

            # Insert fields metadata
            result = Forms.create_form_fields(form_id, fields)
            if isinstance(result, dict):  # Check if error occurred
                return result

            # Create table for form responses
            table_name = Forms.create_dynamic_table(form_name, fields)
            if isinstance(table_name, dict):  # Check if error occurred
                return table_name

            return {"form_id": form_id, "table_name": table_name}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def add_new_field(table_name, field_name, field_type):
        try:
            db_connection = Connection()
            db = db_connection._connect()
            cursor = db.cursor()

            # Generate the appropriate SQL type
            field_sql_type = "VARCHAR(255)" if field_type == "text" else \
                "INT" if field_type == "number" else \
                    "FILE" if field_type == "text" else \
                        "DATE" if field_type == "date" else \
                            "JSON"  # Default for multi-select or dropdown

            query = f"ALTER TABLE {table_name} ADD COLUMN {field_name} {field_sql_type};"
            cursor.execute(query)

            # Commit and close DB connection
            db.commit()
            cursor.close()
            db.close()
            return table_name
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_form_info(task_id):
        """
        Fetch form info by task ID.
        """
        if not task_id:
            raise ValueError("Task ID must be provided and cannot be None or empty.")

        try:
            db_connection = Connection()
            result = db_connection.select_one(
                table_name='forms',
                condition='task_id = %s',
                bind_variables=(task_id,)
            )
            return result
        except ValueError as ve:
            General.write_event(f"Invalid input in get_form_info: {ve}")
            raise
        except Exception as e:
            General.write_event(f"Error in get_form_info: {e}")
            raise

    @staticmethod
    def get_form_fields(form_id):
        """
        Fetch form fields by form ID.
        """
        if not form_id:
            raise ValueError("Form ID must be provided and cannot be None or empty.")

        try:
            db_connection = Connection()
            result = db_connection.select(
                table_name='form_fields',
                condition='form_id = %s',
                bind_variables=(form_id,)
            )
            return result
        except ValueError as ve:
            General.write_event(f"Invalid input in get_form_fields: {ve}")
            raise
        except Exception as e:
            General.write_event(f"Error in get_form_fields: {e}")
            raise

    @staticmethod
    def get_field(field_id):
        if not field_id:
            raise ValueError("Field ID must be provided and cannot be None or empty.")

        try:
            db_connection = Connection()
            result = db_connection.select(
                table_name='form_fields',
                condition='field_id = %s',
                bind_variables=(field_id,)
            )
            return result
        except ValueError as ve:
            # Handle specific errors like invalid input
            General.write_event(f"Invalid input: {ve}")
            raise
        except Exception as e:
            # Log the exception details and re-raise for further handling
            General.write_event(f"An error occurred while fetching form field info: {e}")
            raise
