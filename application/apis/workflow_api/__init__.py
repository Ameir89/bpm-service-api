# application/workflow_api/__init__.py
from flask import Blueprint
workflow_api_blueprint = Blueprint('workflow_api', __name__)

from . import workflow
from . import activities
from . import instances
from . import tasks
from . import execute_template
from . import task_group_workflow
from . import task_group_action
