import os


SQLITE_DB = os.getenv('SQLITE_DB', 'database.db')
SECRET_KEY = os.getenv('SECRET_KEY', 'DEV_TOKEN_DO_NOT_USE')
