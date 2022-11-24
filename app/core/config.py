"""
Global settings for the application
"""
from dotenv import load_dotenv
import os
import platform
from app import project_path

environment = os.getenv('ENV', 'dev')
if environment == 'prod':
    env_path = os.path.join(project_path, 'app', 'core', 'env', 'prod.env')
else:
    env_path = os.path.join(project_path, 'app', 'core', 'env', 'dev.env')

load_dotenv(dotenv_path=env_path)


def sqlite_database_url(db_file_name):
    db_path = os.path.join(project_path, 'db')
    if not os.path.exists(db_path):
        os.makedirs(db_path)
    db_file_path = os.path.join(db_path, db_file_name)
    if platform.system() == 'Linux' or platform.system() == 'Darwin':
        return f'sqlite:////{db_file_path}'
    elif platform.system() == 'Windows':
        return f'sqlite:///{db_file_path}'


class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Not defined")
    PROJECT_VERSION: str = os.getenv("PROJECT_VERSION", "0.0.0")
    SQLALCHEMY_DATABASE_URL: str = sqlite_database_url(os.getenv("SQLALCHEMY_DATABASE_FILE_NAME", "app_dev.db"))


settings = Settings()
