# application/__init__.py
import config
import os
from flask import Flask
from flask_login import LoginManager


login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.debug = True
    environment_configuration = os.environ['CONFIGURATION_SETUP']
    app.config.from_object(environment_configuration)
    login_manager.init_app(app)
    
    
    with app.app_context():
        # Register blueprints

        from application.apis.dynamic_api import dynamic_api_blueprint
        app.register_blueprint(dynamic_api_blueprint)
        from application.apis.seeder_api import seeder_api_blueprint
        app.register_blueprint(seeder_api_blueprint)
        from application.apis.groups_api import groups_api_blueprint
        app.register_blueprint(groups_api_blueprint)
        from application.apis.workflow_api import workflow_api_blueprint
        app.register_blueprint(workflow_api_blueprint)
        from application.apis.auth_api import auth_api_blueprint
        app.register_blueprint(auth_api_blueprint)
        from application.apis.lockups_api import lockups_api_blueprint
        app.register_blueprint(lockups_api_blueprint)

        return app
