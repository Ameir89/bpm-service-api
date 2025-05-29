from collections import defaultdict
import mysql.connector
from mysql.connector.errors import DatabaseError, IntegrityError, InterfaceError, Error
from typing import Optional, Union, List, Dict, Any, Tuple
import config as app
from application.common.general import General


class Connection:
    def __init__(self):
        """Initializes the database connection with configuration values."""
        self._host = app.Config.MYSQL_DATABASE_HOST
        self._user = app.Config.MYSQL_DATABASE_USER
        self._password = app.Config.MYSQL_DATABASE_PASSWORD
        self._db_name = app.Config.MYSQL_DATABASE_DB

    def _connect(self) -> mysql.connector.connection.MySQLConnection:
        """Establishes a connection to the MySQL database.

        Returns:
            MySQLConnection: A connection to the MySQL database.

        Raises:
            ConnectionError: If the connection fails.
        """
        try:
            return mysql.connector.connect(
                host=self._host,
                user=self._user,
                password=self._password,
                database=self._db_name,
            )
        except (DatabaseError, InterfaceError, Error) as err:
            error_message = f"Database connection error: {err}"
            General.write_event(message=error_message)
            raise ConnectionError(error_message)
        except Exception as e:
            error_message = f"Unexpected error during connection: {e}"
            General.write_event(message=error_message)
            raise ConnectionError(error_message)

    def _execute_query(
        self,
        query: str,
        bind_variables: Optional[Tuple] = None,
        fetch_one: bool = False,
        fetch_all: bool = True,
        is_bulk_insert: bool = False,
    ) -> Union[List[Dict[str, Any]], Dict[str, Any], int, None]:
        """Executes a SQL query and handles connection management.

        Args:
            query (str): The SQL query to execute.
            bind_variables (Optional[Tuple]): The bind variables for the query.
            fetch_one (bool): Whether to fetch a single record.
            fetch_all (bool): Whether to fetch all records.
            is_bulk_insert (bool): Whether the query is a bulk insert.

        Returns:
            Union[List[Dict[str, Any]], Dict[str, Any], int, None]: Query results.

        Raises:
            mysql.connector.Error: If a database error occurs.
        """
        try:
            with self._connect() as conn:
                with conn.cursor(dictionary=True) as cur:
                    if is_bulk_insert:
                        cur.executemany(query, bind_variables or ())
                        conn.commit()
                        return cur.rowcount
                    else:
                        cur.execute(query, bind_variables or ())
                        if fetch_one:
                            return cur.fetchone()
                        if fetch_all:
                            return cur.fetchall()
                        conn.commit()
                        if query.strip().lower().startswith(("insert", "update")):
                            return cur.lastrowid
                    return None
        except mysql.connector.Error as err:
            General.write_event(message=f"MySQL Error: {err}, Query: {query}")
            raise

    def create(self, table_name: str, data: Dict[str, Any], debug: bool = False) -> int:
        """Inserts a single record into the database.

        Args:
            table_name (str): The name of the table.
            data (Dict[str, Any]): The data to insert.
            debug (bool): Whether to print debug information.

        Returns:
            int: The ID of the inserted record.

        Raises:
            ValueError: If table_name or data is invalid.
        """
        if not table_name or not data:
            raise ValueError("Table name and data are required.")

        columns = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"

        if debug:
            print(f"Query: {query}, Data: {data}")

        return self._execute_query(query, tuple(data.values()), fetch_one=False, fetch_all=False)

    def create_many(self, table_name: str, data: List[Dict[str, Any]], debug: bool = False) -> int:
        """Inserts multiple records into the database.

        Args:
            table_name (str): The name of the table.
            data (List[Dict[str, Any]]): A list of dictionaries representing records.
            debug (bool): Whether to print debug information.

        Returns:
            int: The number of rows inserted.

        Raises:
            ValueError: If table_name or data is invalid.
            TypeError: If data is not a list of dictionaries.
        """
        if not table_name or not isinstance(data, list) or not data:
            raise ValueError("Table name and non-empty list of data are required.")
        if not all(isinstance(d, dict) for d in data):
            raise TypeError("Each item in data must be a dictionary.")

        all_keys = list(data[0].keys())  # Maintain order from first record
        columns = ', '.join(all_keys)
        placeholders = ', '.join(['%s'] * len(all_keys))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        values = [tuple(d[col] for col in all_keys) for d in data]

        if debug:
            print(f"Query: {query}, Data: {values}")

        return self._execute_query(query, values, is_bulk_insert=True)

    def update(
        self,
        table_name: str,
        condition_column: str,
        condition_value: Any,
        update_data: Dict[str, Any],
        debug: bool = False,
    ) -> int:
        """Updates records in the database.

        Args:
            table_name (str): The name of the table.
            condition_column (str): The column to use in the WHERE clause.
            condition_value (Any): The value to match in the WHERE clause.
            update_data (Dict[str, Any]): The data to update.
            debug (bool): Whether to print debug information.

        Returns:
            int: The number of rows updated.

        Raises:
            ValueError: If table_name, condition_column, or update_data is invalid.
        """
        if not table_name or not condition_column or not update_data:
            raise ValueError("Table name, condition column, and update data are required.")

        set_clause = ', '.join([f"{key} = %s" for key in update_data.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {condition_column} = %s"
        bind_variables = tuple(update_data.values()) + (condition_value,)

        if debug:
            print(f"Query: {query}, Data: {update_data}, Condition: {condition_value}")

        return self._execute_query(query, bind_variables, fetch_one=False, fetch_all=False)

    def select(
        self,
        table_name: str,
        columns: Optional[List[str]] = None,
        condition: Optional[str] = None,
        bind_variables: Optional[Tuple] = None,
        debug: bool = False,
    ) -> List[Dict[str, Any]]:
        """Selects records from the database.

        Args:
            table_name (str): The name of the table.
            columns (Optional[List[str]]): The columns to select.
            condition (Optional[str]): The WHERE clause condition.
            bind_variables (Optional[Tuple]): The bind variables for the condition.
            debug (bool): Whether to print debug information.

        Returns:
            List[Dict[str, Any]]: The selected records.

        Raises:
            ValueError: If table_name is invalid.
        """
        if not table_name:
            raise ValueError("Table name is required.")

        columns_str = ', '.join(columns) if columns else '*'
        query = f"SELECT {columns_str} FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"

        if debug:
            print(f"Query: {query}, Bind Variables: {bind_variables}")

        return self._execute_query(query, bind_variables, fetch_one=False)

    def select_one(
        self,
        table_name: str,
        columns: Optional[List[str]] = None,
        condition: Optional[str] = None,
        bind_variables: Optional[Tuple] = None,
        debug: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Selects a single record from the database.

        Args:
            table_name (str): The name of the table.
            columns (Optional[List[str]]): The columns to select.
            condition (Optional[str]): The WHERE clause condition.
            bind_variables (Optional[Tuple]): The bind variables for the condition.
            debug (bool): Whether to print debug information.

        Returns:
            Optional[Dict[str, Any]]: The selected record, or None if no record is found.

        Raises:
            ValueError: If table_name is invalid.
        """
        if not table_name:
            raise ValueError("Table name is required.")

        columns_str = ', '.join(columns) if columns else '*'
        query = f"SELECT {columns_str} FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
        query += " LIMIT 1"

        if debug:
            print(f"Query: {query}, Bind Variables: {bind_variables}")

        return self._execute_query(query, bind_variables, fetch_one=True)

    def execute_raw(
        self,
        query: str,
        bind_variables: Optional[Tuple] = None,
        debug: bool = False,
    ) -> Union[List[Dict[str, Any]], Dict[str, Any], int, None]:
        """Executes a raw SQL query.

        Args:
            query (str): The raw SQL query.
            bind_variables (Optional[Tuple]): The bind variables for the query.
            debug (bool): Whether to print debug information.

        Returns:
            Union[List[Dict[str, Any]], Dict[str, Any], int, None]: Query results.
        """
        if debug:
            print(f"Raw Query: {query}, Bind Variables: {bind_variables}")

        return self._execute_query(query, bind_variables)