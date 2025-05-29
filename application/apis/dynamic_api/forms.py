from application.common.auth_middleware import token_required
from . import dynamic_api_blueprint
from application.common.general import General
from flask import request, jsonify, abort
from ...models.dynamic.forms import Forms


@dynamic_api_blueprint.route('/api/dynamic/forms/add', methods=['POST'])
@token_required
def add_form_field(current_user):
    try:
        # Parse and validate request
        req = request.get_json(force=True)
        req_validation = General.request_validation(json_data=req, keys=[
            ["task_id", "required", None],
            ["form_name", "required", None],
            ["description", None, None],
            ["fields", "required", None],
        ])

        if req_validation is not None:
            return jsonify({
                'message': 'Request parameter error',
                'data': req_validation,
                'success': False
            }), 400

        # Extract data from request
        task_id = req['task_id']
        form_name = req['form_name']
        description = req.get('description', '')  # Optional
        fields = req['fields']

        # Process form creation
        result = Forms.create_form_with_fields(task_id, form_name, description, fields)
        print(result)
        # Check for errors in result
        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'message': 'Failed to create form',
                'error': result['error'],
                'success': False
            }), 500

        return jsonify({
            'message': 'Form created successfully',
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

@dynamic_api_blueprint.route('/api/dynamic/forms', methods=['POST'])
@token_required
def add_form(current_user):
    """
    Create a new form and store its metadata in the database.

    Expected JSON Body:
        {
            "task_id": int,
            "form_name": str,
            "description": str (optional)
        }

    Returns:
        JSON response with form ID if successful.
    """
    try:
        # Parse JSON body
        req = request.get_json(force=True)

        # Validate input
        validation_errors = General.request_validation(json_data=req, keys=[
            ["task_id", "required", None],
            ["form_name", "required", None],
            ["description", None, None],
        ])

        if validation_errors:
            return jsonify({
                'message': 'Invalid request parameters',
                'errors': validation_errors,
                'success': False
            }), 400

        task_id = req["task_id"]
        form_name = req["form_name"].strip()
        description = req.get("description", "").strip()

        # Call form creation logic
        form_id = Forms.create_metadata(task_id, form_name, description)

        # Check for failure
        if isinstance(form_id, dict) and "error" in form_id:
            return jsonify({
                'message': 'Failed to create form',
                'error': form_id['error'],
                'success': False
            }), 500

        return jsonify({
            'message': 'Form created successfully',
            'data': {"form_id": form_id},
            'success': True
        }), 201

    except ValueError as ve:
        return jsonify({
            "error": "Validation error",
            "message": str(ve),
            "data": None,
            "success": False
        }), 400

    except Exception as e:
        # Log the full exception
        General.write_event(f"Unexpected error in add_form: {e}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e),
            "data": None,
            "success": False
        }), 500


@dynamic_api_blueprint.route('/api/dynamic/field/<int:form_id>', methods=['POST'])
@token_required
def add_field(current_user, form_id):
    """
    Add a new field to the specified form.

    Parameters:
        current_user: Authenticated user from token.
        form_id (int): The ID of the form to add the field to.

    Returns:
        JSON response with success status, message, and added field data or error.
    """
    try:
        # Ensure form_id is valid
        if not isinstance(form_id, int) or form_id <= 0:
            return jsonify({
                "message": "Invalid form ID provided.",
                "success": False
            }), 400

        # Parse JSON input
        req = request.get_json(force=True)

        # Validate required keys
        validation_errors = General.request_validation(json_data=req, keys=[
            ["label", "required", None],
            ["name", "required", None],
            ["placeholder", None, None],
            ["field_type", "required", None],
            ["options", None, None],
            ["required", "required", None],
            ["enabled", "required", None],
        ])

        if validation_errors:
            return jsonify({
                'message': 'Invalid request parameters',
                'errors': validation_errors,
                'success': False
            }), 400

        # Validate 'name' to be slug-friendly (no spaces)
        name = req["name"].strip().replace(" ", "_").lower()
        if not name.isidentifier():
            return jsonify({
                'message': 'Field name must be alphanumeric and underscore only',
                'success': False
            }), 400

        # Build field dictionary
        field_data = {
            "label": req["label"].strip(),
            "name": name,
            "placeholder": req.get("placeholder", "") or None,
            "field_type": req["field_type"],
            "options": req.get("options", "") or None,
            "required": int(req["required"]),
            "enabled": int(req["enabled"])
        }

        # Save field to database
        result = Forms.create_form_field(form_id, field_data)

        # If the result is a dict with an error
        if isinstance(result, dict) and result.get("error"):
            return jsonify({
                'message': 'Failed to add field to form',
                'error': result['error'],
                'success': False
            }), 500

        return jsonify({
            'message': 'Field added successfully',
            'data': result,
            'success': True
        }), 201

    except ValueError as ve:
        return jsonify({
            "error": "Invalid input",
            "message": str(ve),
            "data": None,
            "success": False
        }), 400

    except Exception as e:
        General.write_event(f"Unexpected error in add_field: {e}")
        return jsonify({
            "error": "An internal server error occurred",
            "message": str(e),
            "data": None,
            "success": False
        }), 500

@dynamic_api_blueprint.route('/api/dynamic/field/<int:form_id>/<int:field_id>', methods=['PUT'])
@token_required
def update_field(current_user, form_id, field_id):
    """
    Update an existing field for the specified form.

    Parameters:
        current_user: Authenticated user from token.
        form_id (int): ID of the form.
        field_id (int): ID of the field to update.

    Returns:
        JSON response with success status, message, and updated field data or error.
    """
    try:
        # Validate IDs
        if form_id <= 0 or field_id <= 0:
            return jsonify({
                "message": "Invalid form_id or field_id",
                "success": False
            }), 400

        # Parse JSON input
        req = request.get_json(force=True)

        # Validate required fields
        validation_errors = General.request_validation(json_data=req, keys=[
            ["label", "required", None],
            ["name", "required", None],
            ["placeholder", None, None],
            ["field_type", "required", None],
            ["options", None, None],
            ["required", "required", None],
            ["enabled", "required", None],
        ])
        if validation_errors:
            return jsonify({
                "message": "Invalid request parameters",
                "errors": validation_errors,
                "success": False
            }), 400

        # Clean and prepare field data
        name = req["name"].strip().replace(" ", "_").lower()
        if not name.isidentifier():
            return jsonify({
                'message': 'Field name must be alphanumeric and underscores only',
                'success': False
            }), 400

        field_data = {
            "label": req["label"].strip(),
            "name": name,
            "placeholder": req.get("placeholder", "") or "",
            "field_type": req["field_type"],
            "options": req.get("options", "") or None,
            "required": int(req["required"]),
            "enabled": int(req["enabled"])
        }

        # Call update method
        result = Forms.update_form_field(form_id, field_id, field_data)

        if isinstance(result, dict) and result.get("error"):
            return jsonify({
                "message": "Failed to update field",
                "error": result["error"],
                "success": False
            }), 500

        return jsonify({
            "message": "Field updated successfully",
            "data": result,
            "success": True
        }), 200

    except ValueError as ve:
        return jsonify({
            "message": "Invalid input",
            "error": str(ve),
            "success": False
        }), 400

    except Exception as e:
        General.write_event(f"Unexpected error in update_field: {e}")
        return jsonify({
            "message": "An internal server error occurred",
            "error": str(e),
            "success": False
        }), 500
@dynamic_api_blueprint.route('/api/dynamic/field/<int:form_id>/<int:field_id>', methods=['DELETE'])
@token_required
def delete_field(current_user, form_id, field_id):
    """
    Delete a field from the specified form.

    Parameters:
        current_user: Authenticated user from token.
        form_id (int): ID of the form.
        field_id (int): ID of the field to delete.

    Returns:
        JSON response with success status and message.
    """
    try:
        if form_id <= 0 or field_id <= 0:
            return jsonify({
                "message": "Invalid form_id or field_id",
                "success": False
            }), 400

        result = Forms.delete_form_field(form_id, field_id)

        if isinstance(result, dict) and result.get("error"):
            return jsonify({
                "message": "Failed to delete field",
                "error": result["error"],
                "success": False
            }), 500

        return jsonify({
            "message": "Field deleted successfully",
            "success": True
        }), 200

    except Exception as e:
        General.write_event(f"Unexpected error in delete_field: {e}")
        return jsonify({
            "message": "An internal server error occurred",
            "error": str(e),
            "success": False
        }), 500


@dynamic_api_blueprint.route('/api/dynamic/forms/<int:task_id>', methods=['GET'])
@token_required
def get_form_data(current_user, task_id):
    try:
        # Fetch form data using the task_id
        form_data = Forms.get_form_info(task_id=task_id)

        if not form_data:
            return jsonify({
                'message': 'No form found for the given task ID.',
                'data': None,
                'success': False
            }), 404

        # Fetch fields for the form
        form_fields = Forms.get_form_fields(form_data.get("form_id"))

        return jsonify({
            'message': 'Form data retrieved successfully.',
            'data': {
                'form': form_data,
                'form_fields': form_fields
            },
            'success': True
        }), 200

    except ValueError as ve:
        return jsonify({
            "error": "Invalid input",
            "message": str(ve),
            "data": None,
            "success": False
        }), 400
    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "message": str(e),
            "data": None,
            "success": False
        }), 500


@dynamic_api_blueprint.errorhandler(403)
def forbidden(e):
    return jsonify({
        "message": "Forbidden",
        "error": str(e),
        "data": None,
        "success": False
    }), 403


@dynamic_api_blueprint.errorhandler(404)
def not_found(e):
    return jsonify({
        "message": "Endpoint Not Found",
        "error": str(e),
        "data": None,
        "success": False
    }), 404


@dynamic_api_blueprint.errorhandler(500)
def internal_server_error(e):
    return jsonify({
        "message": "Internal Server Error",
        "error": str(e),
        "data": None,
        "success": False
    }), 500
