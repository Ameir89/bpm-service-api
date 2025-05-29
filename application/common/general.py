from sys import platform
from datetime import datetime
import re
import requests
from werkzeug.security import generate_password_hash
import os


class General:
    def __init__(self):
        pass

    # --------------- Validation Methods ----------------
    @staticmethod
    def validate(data, regex):
        """Generic regex validator"""
        return bool(re.match(regex, data))
    @staticmethod
    def is_empty(value):
        """ Helper function to check if a value is None, empty, or only whitespace. """
        return bool(value and value.strip())

    @staticmethod
    def encrypt_password(password):
        """Encrypt password using a secure hash algorithm."""
        return generate_password_hash(password)

    @staticmethod
    def validate_password(password):
        """Password Validator: 8-20 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special char."""
        reg = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$"
        return General.validate(password, reg)

    @staticmethod
    def validate_email(email):
        """Email Validator."""
        reg = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return General.validate(email, reg)

    @staticmethod
    def validate_phone(phone):
        """Phone Number Validator (Sudan specific)."""
        reg = r'^(\+?249|00249)?(([0-9])[0-9]{8})$'
        return General.validate(phone, reg)

    @staticmethod
    def validate_date(date):
        """Date Validator (YYYY-MM-DD format)."""
        reg = r'\d{4}-\d{2}-\d{2}'
        return General.validate(date, reg)

    @staticmethod
    def is_null(value):
        """Check if value is null or empty."""
        return value if value and str(value).strip() else None

    # --------------- Logging Methods ----------------
    @staticmethod
    def write_event(message, level="ERROR"):
        """Log events to a file with timestamp."""
        time_date = datetime.now()
        date = time_date.strftime("%Y-%m-%d")
        log_dir = "D:\\log" if platform.startswith("win") else "/var/log/tana"

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_path = os.path.join(log_dir, f"bpm-service-{date}.log")
        log_message = f'{time_date} -- {level} -- {message}\n'

        with open(file_path, 'a') as log_file:
            log_file.write(log_message)

    # --------------- Request Validation ----------------
    @staticmethod
    def request_validation(json_data, keys):
        """Validate JSON input data based on provided keys."""
        errors = []
        for key, is_required, field_type in keys:
            value = json_data.get(key)

            # Check required fields
            if is_required and not value:
                errors.append({"param": key, "errorType": "required", "message": f"{key} is required."})
                continue

            # Validate specific types
            if field_type == "email" and value and not General.validate_email(value):
                errors.append({"param": key, "errorType": "invalid_format", "message": f"{key} is not a valid email."})

            elif field_type == "phone" and value and not General.validate_phone(value):
                errors.append({"param": key, "errorType": "invalid_format", "message": f"{key} is not a valid phone number."})

            elif field_type == "date" and value and not General.validate_date(value):
                errors.append({"param": key, "errorType": "invalid_format", "message": f"{key} is not a valid date format."})

            elif field_type == "password" and value and not General.validate_password(value):
                errors.append({"param": key, "errorType": "invalid_format", "message": f"{key} does not meet password requirements."})

        return errors if errors else None

    # --------------- Data Handling ----------------
    @staticmethod
    def convert_to_date(value):
        """Convert a string to a date object."""
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None

    @staticmethod
    def sanitize_string(value):
        """Sanitize and remove unwanted spaces."""
        return value.strip() if value else value

    @staticmethod
    def remove_spaces(value):
        """Remove spaces from a string."""
        return value.replace(" ", "") if value else value

    # --------------- API Calls ----------------
    @staticmethod
    def post_api(api_url, data=None, headers=None):
        """POST API Request."""
        try:
            response = requests.post(api_url, json=data, headers=headers)
            response.raise_for_status()  # Raise HTTPError for bad responses
            return response.json()
        except requests.exceptions.RequestException as e:
            General.write_event(f"API POST Request Failed: {e}")
            return {"error": "API request failed", "details": str(e)}

    @staticmethod
    def call_api(api_url, method='GET', params=None, data=None, headers=None):
        """General API Call."""
        try:
            response = requests.request(method, api_url, params=params, json=data, headers=headers)
            response.raise_for_status()  # Raise HTTPError for bad responses
            return response.json()
        except requests.exceptions.RequestException as e:
            General.write_event(f"API {method} Request Failed: {e}")
            return {"error": "API request failed", "details": str(e)}
