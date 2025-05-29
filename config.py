# config.py
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


class Config:
    SECRET_KEY = "ZETTA-CODE-2025-%00249123211150%-BPMSERVESADMIN"
    TOKEN_HOURS = 1
    MAX_TRY_LOGIN = 5
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # MYSQL DB CONNECTION
    MYSQL_DATABASE_USER = "code"
    MYSQL_DATABASE_PASSWORD = "CodeSD.com"
    MYSQL_DATABASE_DB = "dynamic_workflows_db"
    MYSQL_DATABASE_HOST = "localhost"
    MYSQL_DATABASE_PORT = "3306"


class DevelopmentConfig(Config):
    ENV = "development"
    DEBUG = True


class ProductionConfig(Config):
    ENV = "production"
    DEBUG = False
