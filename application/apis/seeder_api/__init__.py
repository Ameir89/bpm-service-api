# application/seeder_api/__init__.py
from flask import Blueprint


seeder_api_blueprint = Blueprint('seeder_api', __name__)

# from . import routes
from . import seeder
