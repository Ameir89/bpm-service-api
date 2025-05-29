from collections import defaultdict
import mysql.connector
from mysql.connector.errors import DatabaseError, IntegrityError, InterfaceError, Error
import config as app
from application.common.general import General


class Connection:
    def __init__(self):
        self._host = app.Config.MYSQL_DATABASE_HOST
        self._user = app.Config.MYSQL_DATABASE_USER
        self._password = app.Config.MYSQL_DATABASE_PASSWORD
        self._db_name = app.Config.MYSQL_DATABASE_DB

    def _connect(self):
        """Establishes a connection to the MySQL database."""
        try:
            return mysql.connector.connect(
                host=self._host,
                user=self._user,
                password=self._password,
                database=self._db_name,
            )
        except DatabaseError as db_err:
            error_message = f"Database error occurred: {db_err}"
            General.write_event(message=error_message)
            raise ConnectionError(error_message)
        except InterfaceError as iface_err:
            error_message = f"Interface error occurred: {iface_err}"
            General.write_event(message=error_message)
            raise ConnectionError(error_message)
        except Error as err:
            error_message = f"MySQL Error: {err}"
            General.write_event(message=error_message)
            raise ConnectionError(error_message)
        except Exception as e:
            error_message = f"Unexpected error: {e}"
            General.write_event(message=error_message)
            raise ConnectionError(error_message)
        


    def _execute_query(self, query, bind_variables=None, fetch_one=False, fetch_all=True, is_bulk_insert=False):
        """
        Executes a query and handles connection management.

        Args:
            query (str): The SQL query to execute.
            bind_variables (tuple, optional): The bind variables for the query.
            fetch_one (bool, optional): Whether to fetch a single record.
            fetch_all (bool, optional): Whether to fetch all records.

        Returns:
            list[dict] or dict or None: Query results.
        """
        try:
            with self._connect() as conn:
                with conn.cursor(dictionary=True) as cur:
                    if is_bulk_insert:
                        # If it's a bulk insert, use executemany
                        cur.executemany(query, bind_variables)
                        conn.commit()

                        # Return the number of rows inserted
                        return cur.rowcount
                    else:
                        cur.execute(query, bind_variables or ())
                        if fetch_one:
                            return cur.fetchone()
                        if fetch_all:
                            return cur.fetchall()
                        conn.commit()
                        
                        # Return the last inserted ID for INSERT queries
                        if query.strip().lower().startswith("insert") or query.strip().lower().startswith("update"):
                            return cur.lastrowid
                    
                    return None
        except mysql.connector.Error as err:
            General.write_event(message=f"MySQL Error: {err}, Query: {query}")
            raise

    def create(self, table_name, data, debug=False):
        """Inserts a record into the database."""
        if not table_name or not data:
            raise ValueError("Table name and data are required.")

        columns = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"

        if debug:
            print(f"Query: {query}, Data: {data}")
        
        insert_id = self._execute_query(query, tuple(data.values()), fetch_one=False, fetch_all=False)
        return insert_id 

    # def create_many(self, table_name, data, debug=False):
    #     """Inserts multiple records into the database."""
    #     if not table_name or not data:
    #         raise ValueError("Table name and data are required.")

    #     columns = ', '.join({key for d in data for key in d.keys()})
    #     placeholders = ', '.join(['%s'] * len(columns.split(', ')))
    #     query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    #     values = [tuple(d.get(col) for col in columns.split(', ')) for d in data]

    #     if debug:
    #         print(f"Query: {query}, Data: {values}")

    #     return self._execute_query(query, values, fetch_one=False, fetch_all=False)
    def create_many(self, table_name, data, debug=False):
        """Inserts multiple records into the database with error handling."""
        
        # Validate inputs
        if not table_name or not isinstance(data, list) or not data:
            General.write_event("Table name and non-empty list of data are required.")
            raise ValueError("Table name and non-empty list of data are required.")
        
        if not all(isinstance(d, dict) for d in data):
            General.write_event("Each item in data must be a dictionary.")
            raise TypeError("Each item in data must be a dictionary.")

        try:
            # Ensure columns are extracted in a consistent order
            all_keys = list(data[0].keys())  # Maintain order from first record
            columns = ', '.join(all_keys)
            placeholders = ', '.join(['%s'] * len(all_keys))
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

            # Generate values while ensuring correct order
            values = [tuple(d[col] for col in all_keys) for d in data]

            if debug:
                print(f"Query: {query}, Data: {values}")

            # Execute the query (assuming `_execute_query` supports bulk insertion)
            return self._execute_query(query, values, fetch_one=False, fetch_all=False, is_bulk_insert=True)

        except Exception as e:
            General.write_event(f"Unexpected Error: {e}")
            print(f"Unexpected Error: {e}")
            return {"error": str(e)}

    def update(self, table_name, condition_column, condition_value, update_data, debug=False):
        """Updates records in the database."""
        if not table_name or not condition_column or not update_data:
            raise ValueError("Table name, condition column, and update data are required.")

        set_clause = ', '.join([f"{key} = %s" for key in update_data.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {condition_column} = %s"

        if debug:
            print(f"Query: {query}, Data: {update_data}, Condition: {condition_value}")
        
        updated_id = self._execute_query(query, tuple(update_data.values()) + (condition_value,), fetch_one=False, fetch_all=False)
        return updated_id

    def select(self, table_name, columns=None, condition=None, bind_variables=None, debug=False):
        """Selects records from the database."""
        if not table_name:
            raise ValueError("Table name is required.")

        columns_str = ', '.join(columns) if columns else '*'
        query = f"SELECT {columns_str} FROM {table_name}"

        if condition:
            query += f" WHERE {condition}"

        if debug:
            print(f"Query: {query}, Bind Variables: {bind_variables}")

        return self._execute_query(query, bind_variables, fetch_one=False)

    def select_one(self, table_name, columns=None, condition=None, bind_variables=None, debug=False):
        """Selects a single record from the database."""
        
        # Ensure table_name is provided
        if not table_name:
            raise ValueError("Table name is required.")

        # Set columns to '*' if not provided, otherwise join the column names
        columns_str = ', '.join(columns) if columns else '*'
        
        # Build the query
        query = f"SELECT {columns_str} FROM {table_name}"
        
        # Add condition if provided
        if condition:
            query += f" WHERE {condition}"
        
        # Add LIMIT 1 to fetch only one record
        query += " LIMIT 1"

        # Debugging output
        if debug:
            print(f"Query: {query}")
            print(f"Bind Variables: {bind_variables}")

        # Execute the query
        return self._execute_query(query, bind_variables, fetch_one=True)

    def execute_raw(self, query, bind_variables=None, debug=False):
        """Executes a raw SQL query."""
        if debug:
            print(f"Raw Query: {query}, Bind Variables: {bind_variables}")

        return self._execute_query(query, bind_variables)

    def delete(self, table_name, condition, bind_variables=None, debug=False):
        """Deletes records from the database."""
        if not table_name or not condition:
            raise ValueError("Table name and condition are required.")

        query = f"DELETE FROM {table_name} WHERE {condition}"

        if debug:
            print(f"Query: {query}, Bind Variables: {bind_variables}")

        return self._execute_query(query, bind_variables, fetch_one=False, fetch_all=False)

