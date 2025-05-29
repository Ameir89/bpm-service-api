from functools import wraps
import jwt
from flask import request, jsonify, abort
# import config as app
from config import Config
from application.models.auth.users import Users

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Extract token from the Authorization header
        token = None
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            token = auth_header.split(" ")[1] if auth_header.startswith("Bearer ") else None

        # Check if token exists
        if not token:
            return jsonify({
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized",
                "success": False,
                "code": 401
            }), 401

        try:
            # Decode token
            decoded_data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])

            # Fetch user details
            instance_user = Users()
            current_user = instance_user.get_user_by_id(decoded_data["user_id"])

            # Validate if user exists
            if not current_user:
                return jsonify({
                    "message": "Invalid Authentication Token!",
                    "data": None,
                    "error": "Unauthorized",
                    "success": False,
                    "code": 401
                }), 401

            # Check user status (e.g., if user is deactivated)
            if current_user.get("status") == 0:
                return jsonify({
                    "message": "User account is inactive!",
                    "data": None,
                    "error": "Forbidden",
                    "success": False,
                    "code": 403
                }), 403

        except jwt.ExpiredSignatureError:
            # Handle expired token
            return jsonify({
                "message": "Token has expired!",
                "data": None,
                "error": "Unauthorized",
                "success": False,
                "code": 401
            }), 401

        except jwt.InvalidTokenError:
            # Handle other invalid token errors
            return jsonify({
                "message": "Invalid Token!",
                "data": None,
                "error": "Unauthorized",
                "success": False,
                "code": 401
            }), 401

        except Exception as e:
            # Handle other unexpected errors
            return jsonify({
                "message": "An error occurred during authentication.",
                "data": None,
                "error": str(e),
                "success": False,
                "code": 500
            }), 500

        # If token is valid, proceed with the wrapped function
        return f(current_user, *args, **kwargs)

    return decorated
