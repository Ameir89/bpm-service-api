# application/groups_api/__init__.py
from flask import Blueprint
groups_api_blueprint = Blueprint('groups_api', __name__)

from . import groups
