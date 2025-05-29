# application/auth_api/__init__.py
from flask import Blueprint
auth_api_blueprint = Blueprint('auth_api', __name__)

from . import users
from . import roles
from . import permissions
