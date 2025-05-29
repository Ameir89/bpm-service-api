from application.mysql_connection import Connection 
from application.common.general import General
import json

class Lockups:
    def __init__(self):
        pass

    @staticmethod
    def create_metadata(name,display_name, status):
        try:
            db_connection = Connection()
            db = db_connection._connect()
            cursor = db.cursor()
            table_name = f"lkt_{name.lower().replace(' ', '_')}"
            # Insert form metadata
            cursor.execute(
                'INSERT INTO lockups (name,display_name,table_name ,status ) VALUES (%s,%s, %s, %s)',
                (name,display_name,table_name ,status)
            )
            lockup_id = cursor.lastrowid  # Get the inserted form ID

            # Commit and close DB connection
            db.commit()
            cursor.close()
            db.close()
            return lockup_id
        except Exception as e:
            return {"error": str(e)}


    @staticmethod
    def create_dynamic_table(name):
        try:
            db_connection = Connection()
            db = db_connection._connect()
            cursor = db.cursor()

            # Create table based on form name
            table_name = f"lkt_{name.lower().replace(' ', '_')}"
            columns = ["id INT PRIMARY KEY AUTO_INCREMENT"]

            # name = name.replace(' ', '_').lower()
            columns.append(f"name VARCHAR(255)")
            # columns.append(f"display_name VARCHAR(255)")
            columns.append("is_deleted INT DEFAULT 0")
            # Build and execute the CREATE TABLE query
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)});"
            cursor.execute(query)
            
            # Commit and close DB connection
            db.commit()
            cursor.close()
            db.close()
            return table_name
        except Exception as e:
            General.write_event(f"{e}")
            return {"error": str(e)}
        
        

    @staticmethod
    def create_form_with_fields(lockup_name,display_name, status):
        try:
            # Create form metadata
            lockup_id = Lockups.create_metadata(lockup_name,display_name, status)
            if isinstance(lockup_id, dict):  # Check if error occurred
                return lockup_id
         
            # Create table for form responses
            table_name = Lockups.create_dynamic_table(lockup_name)
            if isinstance(table_name, dict):  # Check if error occurred
                return table_name

            
            return {"lockup_id": lockup_id, "table_name": table_name}
        except Exception as e:
            return {"error": str(e)}
       
    @staticmethod   
    def search_lockup_table(search_value):
        """
        Retrieve a lockup's details by its search value.
        """
        if  not search_value:
            return {"error": "search value is required."}
        
        try:
            
            db_connection = Connection()
            
             # Use the '%' wildcard for partial matching with the LIKE operator
            like_pattern = f"%{search_value}%"

            # Add LIMIT and OFFSET for pagination
            condition = "is_deleted = %s AND (name LIKE %s OR display_name LIKE %s)"
            bind_variables = (0, like_pattern,like_pattern)

            result = db_connection.select(table_name='`lockups`',
                                          condition= condition,
                                          bind_variables= bind_variables, 
                                          debug=True
                                          )

            if not result:
                return {"error": f"No data found for table"}

            return {"success": True, "data": result}
           
        except Exception as e:
            General.write_event(f"Error in search name or display name lockup: {e}")
            return {"error": f"Error retrieving lockup: {str(e)}"}
      
      
    @staticmethod
    def get_lockups(page=1, page_size=10):
        try:
             # Zero means except soft deleted
            offset = (page - 1) * page_size  # Calculate the offset

            # Add LIMIT and OFFSET for pagination
            condition = "is_deleted = %s LIMIT %s OFFSET %s"
            bind_variables = (0, page_size, offset)
            
            db_connection = Connection()
            results = db_connection.select(
                table_name='lockups',
                condition=condition,
                bind_variables=bind_variables,
                debug=True
                )
            
            if not results:
                return {"error": "No groups found."}

            # Fetch total count of groups for pagination metadata
            total_count_condition = "is_deleted = %s"
            total_count_results = db_connection.select(
                table_name="`lockups`",
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
            General.write_event(f"Error listing groups: {str(e)}")
            return {"error": f"Error listing groups: {str(e)}"}
    
    @staticmethod
    def update_lockup(id,display_name,status):
        try:
            db_connection = Connection()
            is_update = db_connection.update(
                table_name="`lockups`",
                condition_column="id",
                condition_value=id,
                update_data={"display_name": display_name, "status": status},
                debug=True
            )

            if is_update != 0:
                return {"error": "Failed to update lockup data."}
            return is_update
        except ValueError as ve:
            # Handle specific errors like invalid input
            General.write_event(f"Invalid input: {ve}")
            raise
        except Exception as e:
            # Log the exception details and re-raise for further handling
            General.write_event(f"An error occurred while update lockup data: {e}")
            raise     
    
    
    @staticmethod
    def delete_lockup(id):
        try:
            db_connection = Connection()
            is_update = db_connection.update(
                table_name="`lockups`",
                condition_column="id",
                condition_value=id,
                update_data={"is_deleted": 1},
                debug=True
            )

            if is_update != 0:
                return {"error": "Failed to delete lockup."}
            return is_update
        except ValueError as ve:
            # Handle specific errors like invalid input
            General.write_event(f"Invalid input: {ve}")
            raise
        except Exception as e:
            # Log the exception details and re-raise for further handling
            General.write_event(f"An error occurred while delete lockup: {e}")
            raise     
        
        
    @staticmethod
    def get_lockup_info(lockup_id):
        if not lockup_id:
            General.write_event("Form ID must be provided and cannot be None or empty.")
            raise ValueError("Form ID must be provided and cannot be None or empty.")
        
        try:
            db_connection = Connection()
            result = db_connection.select_one(
                table_name='lockups',
                condition='id = %s AND is_deleted = %s',
                bind_variables=(lockup_id,0)
            )
            return result
        except ValueError as ve:
            # Handle specific errors like invalid input
            General.write_event(f"Invalid input: {ve}")
            raise
        except Exception as e:
            # Log the exception details and re-raise for further handling
            General.write_event(f"An error occurred while fetching form feilds info: {e}")
            raise
    
    @staticmethod
    def create_lockup_data(lockup_id, data):
        try:
            # Validate inputs
            if not lockup_id or not isinstance(data, dict) or not data:
                General.write_event("Invalid table name or data provided")
                return {"error": "Invalid table name or data provided"}
            
            lockup_instance = Lockups()
            lockup = lockup_instance.get_lockup_info(lockup_id)

            if not lockup or "table_name" not in lockup:
                General.write_event("Lockup info not found or invalid")
                return {"error": "Lockup info not found or invalid"}

            table_name = lockup["table_name"]
            db_connection = Connection()
            db = db_connection._connect()
            cursor = db.cursor()

            try:
                # Prepare columns and values dynamically
                columns = ", ".join([f"`{key}`" for key in data.keys()])  # Handle SQL reserved keywords
                placeholders = ", ".join(["%s"] * len(data))
                values = tuple(data.values())

                # Construct query with placeholders
                query = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"
                cursor.execute(query, values)

                # Commit and get the last inserted ID
                db.commit()
                inserted_id = cursor.lastrowid
            finally:
                cursor.close()
                db.close()

            return {"success": True, "id": inserted_id}

        except Exception as e:
            General.write_event(f"Error in create_lockup_data: {e}")
            return {"error": str(e)}
        
        
    @staticmethod   
    def get_lockup_table_data(lockup_id,page,page_size):
        """
        Retrieve a lockup's details by its ID.
        """
        if not lockup_id:
            return {"error": "Lockup ID is required."}
        
        try:
            
            lockup_instance = Lockups()
            lockup = lockup_instance.get_lockup_info(lockup_id)

            if not lockup or "table_name" not in lockup:
                return {"error": "Lockup info not found or invalid."}

            table_name = lockup["table_name"]
            db_connection = Connection()
            
             # Zero means except soft deleted
            offset = (page - 1) * page_size  # Calculate the offset

            # Add LIMIT and OFFSET for pagination
            condition = "is_deleted = %s LIMIT %s OFFSET %s"
            bind_variables = (0, page_size, offset)

            result = db_connection.select(table_name=table_name,
                                          condition= condition,
                                          bind_variables= bind_variables, 
                                          debug=True
                                          )

            if not result:
                return {"error": f"No data found for table: {table_name}"}

            # return {"success": True, "data": result}
            # Fetch total count of groups for pagination metadata
            total_count_condition = "is_deleted = %s"
            total_count_results = db_connection.select(
                table_name= table_name,
                columns=["COUNT(*) as total"],
                condition=total_count_condition,
                bind_variables=(0,)
            )
            total_count = total_count_results[0]["total"] if total_count_results else 0

            # Prepare response with pagination metadata
            return {
                "data": result,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_items": total_count,
                    "total_pages": (total_count + page_size - 1) // page_size
                }
            }

        except Exception as e:
            General.write_event(f"Error in get_lockup_table_data: {e}")
            return {"error": f"Error retrieving lockup: {str(e)}"}
        
     
    @staticmethod   
    def search_lockup_table_data(lockup_id,search_value):
        """
        Retrieve a lockup's details by its ID.
        """
        if not lockup_id or not search_value:
            return {"error": "Lockup ID or search value is required."}
        
        try:
            
            lockup_instance = Lockups()
            lockup = lockup_instance.get_lockup_info(lockup_id)

            if not lockup or "table_name" not in lockup:
                return {"error": "Lockup info not found or invalid."}

            table_name = lockup["table_name"]
            db_connection = Connection()
            
             # Use the '%' wildcard for partial matching with the LIKE operator
            like_pattern = f"%{search_value}%"

            # Add LIMIT and OFFSET for pagination
            condition = "is_deleted = %s AND name LIKE %s"
            bind_variables = (0, like_pattern)

            result = db_connection.select(table_name=table_name,
                                          condition= condition,
                                          bind_variables= bind_variables, 
                                          debug=True
                                          )

            if not result:
                return {"error": f"No data found for table: {table_name}"}

            return {"success": True, "data": result}
           
        except Exception as e:
            General.write_event(f"Error in get_lockup_table_data: {e}")
            return {"error": f"Error retrieving lockup: {str(e)}"}
        
        
    @staticmethod
    def update_lockup_data(lockup_id, id, name):
        try:
            # Validate inputs
            if not all([lockup_id, id, name]):
                General.write_event("Invalid input parameters provided")
                return {"error": "Invalid input parameters provided" ,"success" : False}

            # Fetch lockup information
            lockup_instance = Lockups()
            lockup = lockup_instance.get_lockup_info(lockup_id)

            if not lockup or "table_name" not in lockup:
                General.write_event("Lockup info not found or invalid")
                return {"error": "Lockup info not found or invalid" , "success" : False}

            table_name = lockup["table_name"]

            # Connect to the database
            db_connection = Connection()
            db = db_connection._connect()

            try:
                with db.cursor() as cursor:
                    # Prepare the SQL query dynamically
                    query = f"UPDATE `{table_name}` SET `name` = %s WHERE id = %s"
                    values = (name, id)

                    # Execute the query
                    cursor.execute(query, values)
                    db.commit()

                    # Check if any rows were affected
                    if cursor.rowcount == 0:
                        General.write_event(f"No rows updated for lockup_id: {lockup_id}")
                        return {"error": "No rows updated" , "success" : False}

                    # Return success response
                    return {"row_updated": cursor.rowcount ,"success" : True}

            except Exception as e:
                db.rollback()  # Rollback in case of error
                General.write_event(f"Error updating lockup data: {e}")
                return {"error": str(e) ,"success" : False}

            finally:
                db.close()  # Ensure the connection is closed

        except Exception as e:
            General.write_event(f"Unexpected error in update_lockup_data: {e}")
            return {"error": str(e) ,"success" : False}
        
        
    @staticmethod
    def delete_lockup_data(lockup_id, id):
        try:
            # Validate inputs
            if not all([lockup_id, id]):
                General.write_event("Invalid input parameters provided")
                return {"error": "Invalid input parameters provided"}

            # Fetch lockup information
            lockup_instance = Lockups()
            lockup = lockup_instance.get_lockup_info(lockup_id)

            if not lockup or "table_name" not in lockup:
                General.write_event("Lockup info not found or invalid")
                return {"error": "Lockup info not found or invalid"}

            table_name = lockup["table_name"]

            # Connect to the database
            db_connection = Connection()
            db = db_connection._connect()

            try:
                with db.cursor() as cursor:
                    # Prepare the SQL query dynamically
                    query = f"UPDATE `{table_name}` SET `is_deleted` = %s WHERE id = %s"
                    values = (1, id)

                    # Execute the query
                    cursor.execute(query, values)
                    db.commit()

                    # Check if any rows were affected
                    if cursor.rowcount == 0:
                        General.write_event(f"No rows deleted for lockup_id: {lockup_id}")
                        return {"error": "No rows deleted"}

                    # Return success response
                    return {"success": True, "rows_deleted": cursor.rowcount}

            except Exception as e:
                db.rollback()  # Rollback in case of error
                General.write_event(f"Error deleted lockup data: {e}")
                return {"error": str(e)}

            finally:
                db.close()  # Ensure the connection is closed

        except Exception as e:
            General.write_event(f"Unexpected error in upddeleted lockup data: {e}")
            return {"error": str(e)}
        