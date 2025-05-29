from application.mysql_connection import Connection
from application.common.general import General
from datetime import datetime
from typing import Union, Dict

class Process:
    def __init__(self):
        self.db_connection = Connection()

    """
        Create a new workflow process.
    """

    def create_process(self, instance_id, task_id, status, assigned_to, group_id=None, level_id=None):
        if not instance_id or not task_id:
            return {"error": "workflow instance or task is required.",
                    "success": False}

        try:
            started_at = datetime.now()
            data = {
                "instance_id": instance_id,
                "task_id": task_id,
                "status": status,
                "assigned_to": assigned_to,
                "started_at": started_at,
                "group_id": group_id,
                "level_id": level_id
            }

            process_id = self.db_connection.create("`workflow_process`", data, debug=True)
            print(process_id)
            if not process_id:
                return {"error": "Failed to create workflow process.", "success": False}

            return {"task_id": task_id, "success": True}
        except Exception as e:
            General.write_event(f"Error creating workflow process: {str(e)}")
            return {"error": f"Error creating workflow process: {str(e)}", "success": False}

    """
    Retrieve a workflow process associated with a specific instance.
    """
    def get_process(self, instance_id: (int, str), status: str = None) -> dict:
        """
        Retrieve a workflow process associated with a specific instance.

        Args:
            instance_id (int, str): Required identifier for the instance. Must be a non-empty value.
            status (str, optional): Filter processes by status. Defaults to None.

        Returns:
            dict: A dictionary containing:
                - success (bool): Indicates if the operation was successful.
                - data (list|None): Retrieved process data or None if not found/error.
                - error (str|None): Error message if unsuccessful.

        Example:
            # >>> response = obj.get_process(123)
            # >>> if response['success']:
            # >>>     print(response['data'])
        """
        # Input validation
        if not instance_id and instance_id != 0:  # Allow 0 as valid ID
            return {
                "success": False,
                "data": None,
                "error": "Instance ID must be a non-empty value"
            }

        try:
            # Build query parameters
            query_params = {
                'table_name': 'workflow_process',
                'condition': 'instance_id = %s',
                'bind_variables': (instance_id,)
            }

            if status is not None:
                query_params['condition'] += ' AND status = %s'
                query_params['bind_variables'] += (status,)

            # Execute query
            result = self.db_connection.select(**query_params)

            if not result:
                return {
                    "success": True,
                    "data": None,
                    "error": None
                }

            return {
                "success": True,
                "data": result,
                "error": None
            }

        except Exception as e:
            # Log full error details with instance context
            error_msg = f"Error retrieving workflow process for instance {instance_id}: {str(e)}"
            General.write_event(error_msg)

            # Return sanitized error to caller
            return {
                "success": False,
                "data": None,
                "error": "Failed to retrieve workflow process. Please check logs."
            }

    """ function Update the status of a workflow process and optionally set completion time. """
    def update_process(self, process_id: Union[int, str], status: str) -> Dict[str, Union[bool, str, int, None]]:
        """
        Update the status of a workflow process and optionally set completion time.

        Args:
            process_id (int | str): The ID of the process to update. Must be a positive integer or non-empty string.
            status (str): New status for the process. Must be one of ["Pending", "Processing", "Completed", "Failed"]

        Returns:
            dict: Contains:
                - success (bool): Indicates if the update was successful
                - data (int | None): Number of affected rows if successful
                - error (str | None): Error message if unsuccessful

        Example:
            # >>> result = workflow.update_process(123, "Completed")
            # >>> if result['success']:
            # >>>     print(f"Updated {result['data']} records")
        """
        # Input validation
        allowed_statuses = {"Pending", "Processing", "Completed", "Failed"}

        # Validate process_id
        if (not process_id and process_id != 0) or \
                (isinstance(process_id, str) and not process_id.strip()):
            return {
                "success": False,
                "data": None,
                "error": "Valid process ID is required"
            }

        # Validate status
        if status not in allowed_statuses:
            return {
                "success": False,
                "data": None,
                "error": f"Invalid status. Allowed values: {', '.join(allowed_statuses)}"
            }

        try:
            # Use UTC time for database consistency
            current_time = datetime.now()
            update_data = {
                "status": status,
                "completed_at": current_time if status in ("Completed", "Failed") else None
            }

            # Execute update
            affected_rows = self.db_connection.update(
                table_name="workflow_process",
                condition_column="id",
                condition_value=process_id,
                update_data=update_data
            )

            # Check if update was applied
            if affected_rows == 0:
                return {
                    "success": False,
                    "data": 0,
                    "error": "No process found with the specified ID"
                }

            # Log successful update
            General.write_event(f"Updated process {process_id} to status {status}")

            return {
                "success": True,
                "data": affected_rows,
                "error": None
            }

        except Exception as e:
            # Log full error details with context
            error_msg = f"Failed updating process {process_id}: {str(e)}"
            General.write_event(error_msg)

            # Return generic error to client
            return {
                "success": False,
                "data": None,
                "error": "Failed to update process. Please check system logs."
            }

    def get_process_by_id(self, process_id: (int, str)) -> dict:
        """
        Retrieve a workflow process associated with a specific instance.

        Args:
            process_id (int, str): Required identifier for the instance. Must be a non-empty value.


        Returns:
            dict: A dictionary containing:
                - success (bool): Indicates if the operation was successful.
                - data (list|None): Retrieved process data or None if not found/error.
                - error (str|None): Error message if unsuccessful.

        Example:
            # >>> response = obj.get_process(123)
            # >>> if response['success']:
            # >>>     print(response['data'])
        """
        # Input validation
        if not process_id and process_id != 0:  # Allow 0 as valid ID
            return {
                "success": False,
                "data": None,
                "error": "Instance ID must be a non-empty value"
            }

        try:
            # Build query parameters
            query_params = {
                'table_name': 'workflow_process',
                'condition': 'id = %s',
                'bind_variables': (process_id,)
            }

            # Execute query
            result = self.db_connection.select_one(**query_params)

            if not result:
                return {
                    "success": True,
                    "data": None,
                    "error": None
                }

            return {
                "success": True,
                "data": result,
                "error": None
            }

        except Exception as e:
            # Log full error details with instance context
            error_msg = f"Error retrieving workflow process for id {process_id}: {str(e)}"
            General.write_event(error_msg)

            # Return sanitized error to caller
            return {
                "success": False,
                "data": None,
                "error": "Failed to retrieve workflow process. Please check logs."
            }

