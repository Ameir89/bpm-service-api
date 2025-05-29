from datetime import datetime, timedelta
import json
import jwt
# import config as app
from config import Config
from . import auth_api_blueprint
from application.common.general import General
from flask import app, request, jsonify, abort
from ...models.auth.roles import Roles
from werkzeug.security import generate_password_hash,check_password_hash
from application.common.auth_middleware import token_required

      
        
"""Add Role API."""

@auth_api_blueprint.route('/api/roles/add', methods=['POST'])
# @token_required
def add_role():
    try:
        req = request.get_json(force=True)
        req_validation = General.request_validation(json_data=req, keys=[
            ["name", "required", None],
            ["display_name", None, None],
            ["parent_role", None, None],
            ["description", None, None],
            ["permissions", None, None],
        ])

        if req_validation is not None:
            return jsonify({
                'message': 'Request parameter error',
                'data': req_validation,
                'success': False
            }), 400

        name = req['name']
        display_name = req['display_name']
        parent_role = req.get('parent_role', 0) 
        description = req.get('description')
        permissions = req.get('permissions', None)  # Convert options to tuble

        # Validate required fields
        if not name :
            return jsonify({'message': 'Username, password, and confirm password are required'}), 400

        # Check if the username already exists
        instance_role = Roles()
        # Create the role
        result = instance_role.create_role(
           name=name,
           parent_role=parent_role,
           display_name=display_name,  
           description=description,
           permissions= permissions,
        )

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to create role',
                'error': result['error'],
                'success': False
            }), 500

        return jsonify({
            'message': 'Role created successfully',
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


# """update Role API."""
# @auth_api_blueprint.route('/api/roles/<int:role_id>/update', methods=['PATCH'])
# # @token_required
# def update_role(role_id):
#     try:
#         req = request.get_json(force=True)
#         req_validation = General.request_validation(json_data=req, keys=[
#             ["username", None, None],
#             ["group", None, None],
#             ["level", None, None],
#             ["role", None, None],
#             ["status", None, None],
#         ])

#         if req_validation is not None:
#             return jsonify({
#                 'message': 'Request parameter error',
#                 'data': req_validation,
#                 'success': False
#             }), 400

#         username = req['username']
#         group = req['group']
#         level = req['level']
#         role = req['role']
#         status = req['status']
#         user = Users()
#         result = user.update_user_data(user_id,username,group,level,role,status)

#         if isinstance(result, dict) and 'error' in result:
#             return jsonify({
#                 'message': 'Failed to update user',
#                 'error': result['error'],
#                 'success': False
#             }), 500

#         return jsonify({
#             'message': 'Usre updated successfully',
#             'data': result,
#             'success': True
#         }), 200

#     except Exception as e:
#         return jsonify({
#             "error": "An internal server error occurred",
#             "message": str(e),
#             "data": None,
#             "success": False
#         }), 500

"""get roles by id API."""
@auth_api_blueprint.route('/api/roles/<int:role_id>', methods=['GET'])
# @token_required
def get_role(role_id):
    try:
        role = Roles()
        result = role.get_role_by_id(role_id)

        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to retrieve role info',
                'error': result['error'],
                'success': False
            }), 404

        return jsonify({
            'message': 'Successfully retrieved role info',
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
@auth_api_blueprint.route('/api/roles/<int:role_id>', methods=['DELETE'])
@token_required
def delete_role_by_id(current_user, role_id):
    """
    API endpoint to delete a user by ID.
    """
    try:
        # Ensure the current user is authorized to delete users
        
        if current_user['role'] != 1 and current_user['role'] != 2:
            return jsonify({
                "message": "You are not authorized to delete roles.",
                "success": False
            }), 403

        # Validate user ID
        if role_id <= 0:
            return jsonify({
                "message": "Invalid role ID",
                "success": False
            }), 400

        # Create a Users instance and delete the user
        role_instance = Roles()
        result = role_instance.delete_role(role_id)

        # Handle deletion failure
        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                "message": "Failed to delete role",
                "error": result['error'],
                "success": False
            }), 500

        # Handle case where role was not found
        if result == 0:
            return jsonify({
                "message": "Role not found",
                "data": {"role_id": role_id},
                "success": False
            }), 404

        return jsonify({
            "message": "Role deleted successfully",
            "data": {"role_id": role_id},
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


"""return list of roles API."""
@auth_api_blueprint.route('/api/roles/<int:page>&<int:page_size>', methods=['GET'])
# @token_required
def list_roles(page,page_size):
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
        role = Roles()
        result = role.list_roles(page, page_size)
        # print(result)
        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to retrieve list of roles',
                'error': result['error'],
                'success': False
            }), 500

        return jsonify({
            'message': 'Successfully retrieved list of roles',
            'data': result['data'],  # Pass the roless data
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


# """change password API."""

# @auth_api_blueprint.route('/api/users/<int:user_id>/change-password', methods=['PUT'])
# # @token_required
# def change_password(user_id):
#     try:
#         # Parse request body
#         req = request.get_json(force=True)
#         old_password = req.get('old_password')
#         new_password = req.get('new_password')
#         confirm_password = req.get('confirm_password')

#         # Validate inputs
#         if not old_password or not new_password or not confirm_password:
#             return jsonify({
#                 "message": "Old password, new password, and confirm password are required",
#                 "success": False
#             }), 400

#         if new_password != confirm_password:
#             return jsonify({
#                 "message": "New password and confirm password do not match",
#                 "success": False
#             }), 400
#         instance_user = Users()
#         user = instance_user.get_user_by_id(user_id)

#         if not user:
#             return jsonify({
#                 "message": "User not found",
#                 "success": False
#             }), 404

#         # Verify old password
#         if not check_password_hash(user['password'], old_password):
#             return jsonify({
#                 "message": "Old password is incorrect",
#                 "success": False
#             }), 400

#         # Hash the new password
#         hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')

#         # Update the user's password
#         result = instance_user.update_user_password(user_id, hashed_password)

#         if isinstance(result, dict) and 'error' in result:
#             return jsonify({
#                 "message": "Failed to change password",
#                 "error": result['error'],
#                 "success": False
#             }), 500

#         return jsonify({
#             "message": "Password changed successfully",
#             "success": True
#         }), 200

#     except ValueError as ve:
#         return jsonify({
#             "error": "Invalid input provided",
#             "message": str(ve),
#             "data": None,
#             "success": False
#         }), 400

#     except Exception as e:
#         General.write_event(f"Error in change_password endpoint: {e}")
#         return jsonify({
#             "error": "An internal server error occurred",
#             "message": str(e),
#             "data": None,
#             "success": False
#         }), 500

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
