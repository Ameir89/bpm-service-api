from datetime import datetime, timedelta
import jwt
# import config as app
from config import Config
from . import auth_api_blueprint
from application.common.general import General
from flask import app, request, jsonify, abort
from ...models.auth.users import Users
from ...models.auth.permissions import Permissions
from werkzeug.security import generate_password_hash,check_password_hash
from application.common.auth_middleware import token_required

"""login API."""
@auth_api_blueprint.route('/api/users/login', methods=['POST'])
def login():
    try:
        req = request.get_json(force=True)
        req_validation = General.request_validation(json_data=req, keys=[
            ["username", "required", None],
            ["password", "required", None],
        ])

        if req_validation is not None:
            return jsonify({
                'message': 'Request parameter error',
                'data': req_validation,
                'success': False
            }), 400
            
        # Parse request body    
        username = req.get('username')
        password = req.get('password')
        

        # Validate inputs
        if not username or not password:
            return jsonify({
                "message": "Username and password are required",
                "success": False
            }), 400
        instance_user = Users()
        user_date = instance_user.get_user_by_username_for_login(username)
        if not user_date["success"]:
            return jsonify({
                "message": "User not found",
                "success": False
            }), 404
        user = user_date["data"]
        # Fetch associated permissions
        instance_permission = Permissions()
        permissions = instance_permission.get_permission_by_role_id(role_id=user["role"])
        # Add permissions to role details
        # data["permissions"] = permissions if permissions else []
        
        # Verify password
        if not check_password_hash(user['password'], password):
            return jsonify({
                "message": "Invalid password",
                "success": False
            }), 401

        # Generate token (placeholder logic, replace with real token generation)
        # Calculate the expiration time (1 hour from now)
        expiration_time = datetime.now() + timedelta(hours= Config.TOKEN_HOURS)
        # Create the JWT payload
        payload = {'user_id': user["id"],'exp': expiration_time}
        token = jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")
        
        return jsonify({
            "message": "Login successful",
            "data": {
                "token": token,
                "user": {
                    "id": user['id'],
                    "username": user['username'],
                    "group": user['group_name'],
                    "level_id": user['level'],
                    "level": user['level_name'],
                    "role_id": user['role'],
                    "role": user['role_name'],
                    "status": user['status'],
                    "permissions": permissions if permissions else [],
                }
            },
            "success": True
        }), 200

    except ValueError as ve:
        return jsonify({
            "error": "Invalid input provided",
            "message": str(ve),
            "data": None,
            "success": False
        }), 400

    except Exception as e:
        General.write_event(f"Error in login endpoint: {e}")
        return jsonify({
            "error": "An internal server error occurred",
            "message": str(e),
            "data": None,
            "success": False
        }), 500
        
        
"""register User API."""

@auth_api_blueprint.route('/api/users/register', methods=['POST'])
@token_required
def register(current_user):
    try:
        req = request.get_json(force=True)
        req_validation = General.request_validation(json_data=req, keys=[
            ["full_name", "required", None],
            ["username", "required", None],
            ["password", "required", None],
            ["confirm_password", "required", None],
            ["role", None, None],
            ["group", None, None],
            ["status", None, None],
        ])

        if req_validation is not None:
            return jsonify({
                'message': 'Request parameter error',
                'data': req_validation,
                'success': False
            }), 400
        
        full_name = req['full_name']
        username = req['username']
        password = req['password']
        confirm_password = req['confirm_password']
        role = req.get('role')
        level = req.get('level')
        group = req.get('group', 0)  # Default group to 0 if not provided
        status = req.get('status', 1)  # Default status to 0 if not provided
        created_by = current_user["id"]  # Placeholder for session user ID

        # Validate required fields
        if not full_name or not username or not password or not confirm_password:
            return jsonify({'message': 'Username, password, and confirm password are required','success':False}), 400

        # Check password confirmation
        if password != confirm_password:
            return jsonify({'message': 'Password and confirm password do not match' ,'success':False}), 400

        # Check if the username already exists
        instance_user = Users()
        user =instance_user.get_user_by_username(username)
        print(user)
        if user:
            return jsonify({'message': 'Username already exists' , 'success':False}), 400

        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Create the user
        result = instance_user.create_user(
            full_name= full_name,
            username=username,
            password=hashed_password,
            group=group,
            level=level,
            role=role,
            status=status,
            created_by=created_by
        )

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to create user',
                'error': result['error'],
                'success': False
            }), 500

        return jsonify({
            'message': 'User created successfully',
            'data': result,
            'success': True
        }), 201

    except Exception as e:
        General.write_event(f"Error in register endpoint: {e}")
        return jsonify({
            "error": "An internal server error occurred",
            "message": str(e),
            "data": None,
            "success": False
        }), 500


"""update user API."""
@auth_api_blueprint.route('/api/users/<int:user_id>/update', methods=['PUT'])
@token_required
def update_user(current_user,user_id):
    try:
        req = request.get_json(force=True)
        req_validation = General.request_validation(json_data=req, keys=[
            ["full_name", None, None],
            ["username", None, None],
            ["password", None, None],
            ["confirm_password", None, None],
            ["group", None, None],
            ["level", None, None],
            ["role", None, None],
            ["status", None, None],
        ])

        if req_validation is not None:
            return jsonify({
                'message': 'Request parameter error',
                'data': req_validation,
                'success': False
            }), 400

        full_name = req['full_name']
        username = req['username']
        password = req['password']
        confirm_password = req['confirm_password']
        group = req['group']
        level = req['level']
        role = req['role']
        status = req['status']
        user = Users()
        hashed_password = None
        # Validate inputs
        if  all(map(General.is_empty, [password, confirm_password])):
             # Check password confirmation
            if password != confirm_password:
                return jsonify({'message': 'Password and confirm password do not match'}), 400
            # Hash the password
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
       
           
        
        result = user.update_user_data(user_id,full_name,username,group,level,role,status ,hashed_password)
            
        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to update user',
                'error': result['error'],
                'success': False
            }), 500

        return jsonify({
            'message': 'Usre updated successfully',
            'data': result,
            'success': True
        }), 200

    except Exception as e:
        return jsonify({
            "error": "An internal server error occurred",
            "message": str(e),
            "data": None,
            "success": False
        }), 500

"""get users by id API."""
@auth_api_blueprint.route('/api/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(current_user,user_id):
    try:
        user = Users()
        result = user.get_user_by_id(user_id=user_id)

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to retrieve user info',
                'error': result['error'],
                'success': False
            }), 404

        return jsonify({
            'message': 'Successfully retrieved user info',
            'data': result,
            'success': True
        }), 200

    except Exception as e:
        return jsonify({
            "error": "An internal server error occurred",
            "message": str(e),
            "data": None,
            "success": False
        }), 500


"""delete user by id API."""
@auth_api_blueprint.route('/api/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user_by_id(current_user,user_id):
    """
    API endpoint to delete a user by ID.
    """
    try:
        # Ensure the current user is authorized to delete users
        print(current_user)
        if current_user['role_id'] != 1 and current_user['role_id'] != 2:
            return jsonify({
                "message": "You are not authorized to delete users.",
                "success": False
            }), 403

        # Validate user ID
        if user_id <= 0:
            return jsonify({
                "message": "Invalid user ID",
                "success": False
            }), 400

        # Create a Users instance and delete the user
        user_instance = Users()
        result = user_instance.delete_user(user_id)

        # Handle deletion failure
        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                "message": "Failed to delete user",
                "error": result['error'],
                "success": False
            }), 500

        # Handle case where user was not found
        if result == 0:
            return jsonify({
                "message": "User not found",
                "data": {"user_id": user_id},
                "success": False
            }), 404

        return jsonify({
            "message": "User deleted successfully",
            "data": {"user_id": user_id},
            "success": True
        }), 200

    except ValueError as ve:
        return jsonify({
            "error": "Invalid input provided",
            "message": str(ve),
            "data": None,
            "success": False
        }), 400

    except Exception as e:
        General.write_event(f"Error in delete_user_by_id endpoint: {e}")
        return jsonify({
            "error": "An internal server error occurred",
            "message": str(e),
            "data": None,
            "success": False
        }), 500


"""return list of users API."""
@auth_api_blueprint.route('/api/users/<int:page>&<int:page_size>', methods=['GET'])
@token_required
def list_users(current_user,page,page_size):
    try:
       
        # Validate that page and page_size are integers and positive
        if not isinstance(page, int) or page < 1:
            return jsonify({
                'message': 'Invalid page parameter. Page must be a positive integer.',
                'success': False
            }), 400

        if not isinstance(page_size, int) or page_size < 1 or page_size > 100:
            return jsonify({
                'message': 'Invalid page_size parameter. Page size must be a positive integer between 1 and 100.',
                'success': False
            }), 400

        # Call Groups service to fetch paginated data
        user = Users()
        result = user.list_users(page, page_size)
        # print(result)
        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to retrieve list of users',
                'error': result['error'],
                'success': False
            }), 500

        return jsonify({
            'message': 'Successfully retrieved list of groups',
            'data': result['data'],  # Pass the users data
            'pagination': result['pagination'],  # Include pagination metadata
            'success': True
        }), 200

    except Exception as e:
        return jsonify({
            "error": "An internal server error occurred",
            "message": str(e),
            "data": None,
            "success": False
        }), 500


"""change password API."""

@auth_api_blueprint.route('/api/users/<int:user_id>/change-password', methods=['PUT'])
@token_required
def change_password(current_user,user_id):
    try:
        # Parse request body
        req = request.get_json(force=True)
        old_password = req.get('old_password')
        new_password = req.get('new_password')
        confirm_password = req.get('confirm_password')

        # Validate inputs
        if not old_password or not new_password or not confirm_password:
            return jsonify({
                "message": "Old password, new password, and confirm password are required",
                "success": False
            }), 400

        if new_password != confirm_password:
            return jsonify({
                "message": "New password and confirm password do not match",
                "success": False
            }), 400
        instance_user = Users()
        user = instance_user.get_user_by_id(user_id)

        if not user:
            return jsonify({
                "message": "User not found",
                "success": False
            }), 404

        # Verify old password
        if not check_password_hash(user['password'], old_password):
            return jsonify({
                "message": "Old password is incorrect",
                "success": False
            }), 400

        # Hash the new password
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')

        # Update the user's password
        result = instance_user.update_user_password(user_id, hashed_password)

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                "message": "Failed to change password",
                "error": result['error'],
                "success": False
            }), 500

        return jsonify({
            "message": "Password changed successfully",
            "success": True
        }), 200

    except ValueError as ve:
        return jsonify({
            "error": "Invalid input provided",
            "message": str(ve),
            "data": None,
            "success": False
        }), 400

    except Exception as e:
        General.write_event(f"Error in change_password endpoint: {e}")
        return jsonify({
            "error": "An internal server error occurred",
            "message": str(e),
            "data": None,
            "success": False
        }), 500

@auth_api_blueprint.route('/api/users/search/<string:value>', methods=['GET'])
@token_required
def search_user(current_user, value):
    try:
        # Validate input
        if not value.strip():  # Check if value is empty or only spaces
            return generate_response("Search value is required", success=False, status_code=400)

        instance_user = Users()
        user = instance_user.search_user_name(search_value=value)

        # Handle errors returned from search_user_name
        if isinstance(user, dict) and 'error' in user:
            return generate_response("User retrieval failed", error=user['error'], success=False, status_code=500)

        # Handle case when no user is found
        if not user or (isinstance(user, list) and len(user) == 0):
            return generate_response("User not found", success=False, status_code=404)

        return generate_response("Successfully retrieved user data", data=user, success=True, status_code=200)

    except ValueError as ve:
        return generate_response("Invalid input provided", error=str(ve), success=False, status_code=400)

    except Exception as e:
        General.write_event(f"Error in search_user endpoint: {e}")
        return generate_response("An internal server error occurred", error=str(e), success=False, status_code=500)

def generate_response(message, data=None, error=None, success=True, status_code=200):
    """ Helper function to generate JSON responses consistently """
    response = {
        "message": message,
        "success": success
    }
    if data is not None:
        response["data"] = data
    if error is not None:
        response["error"] = error
    
    return jsonify(response), status_code

@auth_api_blueprint.errorhandler(403)
def forbidden(e):
    return jsonify({
        "message": "Forbidden",
        "error": str(e),
        "data": None,
        "success": False
    }), 403
    
@auth_api_blueprint.errorhandler(404)
def not_found(e):
    return jsonify({
        "message": "Endpoint Not Found",
        "error": str(e),
        "data": None,
        "success": False
    }), 404

@auth_api_blueprint.errorhandler(500)
def internal_server_error(e):
    return jsonify({
        "message": "Internal Server Error",
        "error": str(e),
        "data": None,
        "success": False
    }), 500
