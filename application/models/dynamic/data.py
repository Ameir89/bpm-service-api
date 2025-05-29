from application.mysql_connection import Connection 
from ...common.general import General
import json
import logging

class Data:
    def __init__(self):
        pass

    @staticmethod
    def create_form_data(table_name, data):
        try:
            # Validate inputs
            if not table_name or not isinstance(data, dict) or not data:
                return {"error": "Invalid table name or data provided"}

            db_connection = Connection()
            db = db_connection._connect()
            cursor = db.cursor()

            # Prepare columns and values dynamically
            columns = ", ".join([f"`{key}`" for key in data.keys()])  # Handle SQL reserved keywords
            placeholders = ", ".join(["%s"] * len(data))
            values = tuple(data.values())

            # Construct query with placeholders
            query = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"
            cursor.execute(query, values)

            # Commit and close DB connection
            db.commit()
            inserted_id = cursor.lastrowid  # Get the last inserted ID
            cursor.close()
            db.close()
            return {"success": True, "id": inserted_id}

        except Exception as e:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals():
                db.close()
            return {"error": str(e)}


    @staticmethod
    def fetch_form_data(table_name, columns=None, limit=None, offset=None):
        try:
            # Validate the table name to avoid SQL injection risks
            """
            Table Name Validation: You should replace the list allowed_tables 
            with the actual list of table names that can be queried dynamically. 
            This is to avoid allowing arbitrary table names, which could be a security risk.
            
            """
            allowed_tables = ["table1", "table2", "table3"]  # Example: A list of allowed table names
            if table_name not in allowed_tables:
                raise ValueError("Invalid table name")

            # Establish the database connection
            db_connection = Connection()
            db = db_connection._connect()
            
            # Default columns to fetch all if not provided
            if columns is None:
                columns = "*"
            else:
                # Sanitize columns input (e.g., ensure no SQL injection risks)
                columns = ", ".join([f"`{col}`" for col in columns])  # Handle reserved keywords

            # Construct the SQL query
            query = f"SELECT {columns} FROM `{table_name}`"
            
            # Add LIMIT and OFFSET for pagination if provided
            if limit is not None:
                query += f" LIMIT {limit}"
            if offset is not None:
                query += f" OFFSET {offset}"

            # Execute the query
            with db.cursor(dictionary=True) as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()

            # Close the connection
            db.close()

            return rows

        except Exception as e:
            General.write_event(f"Error fetching data from {table_name}: {e}")
            logging.error(f"Error fetching data from {table_name}: {e}")
            return {"error": str(e), "message": "An error occurred while fetching data"}


    # Fetching all columns and all rows from 'form_customer_feedback'
    # result = fetch_form_data("form_customer_feedback")
    # print(result)

    # Fetching specific columns ('name', 'age') with pagination (limit 10, offset 0)
    # result = fetch_form_data("form_customer_feedback", columns=["name", "age"], limit=10, offset=0)
    # print(result)
