import os

import logging

logger = logging.getLogger(__name__)

SQLITE_DB = os.getenv('SQLITE_DB', 'database.db')
SECRET_KEY = os.getenv('SECRET_KEY', 'DEV_TOKEN_DO_NOT_USE')

if SECRET_KEY == 'DEV_TOKEN_DO_NOT_USE':  # noqa S105
    logger.warning(
        'SECRET_KEY is not set. This is a development environment. '
        'Please set SECRET_KEY in production to a random string.'
    )
