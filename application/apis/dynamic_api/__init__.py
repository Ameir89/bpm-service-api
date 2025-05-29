# application/dynamic_api/__init__.py
from flask import Blueprint
dynamic_api_blueprint = Blueprint('dynamic_api', __name__)

from . import forms
from . import data
from . import lockups