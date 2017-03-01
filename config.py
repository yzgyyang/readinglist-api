import os

###############################################################################
# DEFAULTS
# Any environment variables with the same name as the variables in this section
# will override the value set here
###############################################################################

READING_LIST_DB_URL = 'mysql://build:build@localhost/readinglist?charset=utf8&use_unicode=0'
SECRET_KEY = 'the quick brown fox jumps over the lazy dog'

###############################################################################
# ENVIRONMENT
# Set configuration items from the environment
###############################################################################
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Database connection URL
if os.environ.get('READING_LIST_DB_URL', False):
    SQLALCHEMY_DATABASE_URI = os.environ['READING_LIST_DB_URL']
else:
    SQLALCHEMY_DATABASE_URI = READING_LIST_DB_URL
