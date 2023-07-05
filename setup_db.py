import os
import django
import logging

# Setup django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FlightProject.settings") 
django.setup()

logger = logging.getLogger('django')

def get_connection():
    """Creates and returns a Connection object (from mysql_connector_python) with the default django database settings

    Returns:
        PooledMySQLConnection | MySQLConnection | Any: A Connection object
    """
    from FlightProject.settings import DATABASES
    from mysql.connector import connect
    DATABASE_SETTINGS = DATABASES['default']
    connection = connect(
        host=DATABASE_SETTINGS['HOST'],
        port=DATABASE_SETTINGS['PORT'],
        user=DATABASE_SETTINGS['USER'],
        password=DATABASE_SETTINGS['PASSWORD'],
    )
    if connection:
        logger.info(f"Successfully connected to database @ //{ DATABASE_SETTINGS['HOST'] }:{ DATABASE_SETTINGS['PORT'] }/")
    return connection


def create_schema():
    """Creates the main django schema
    """
    from FlightProject.settings import DATABASES
    
    DATABASE_SETTINGS = DATABASES['default']
    try:
        connection = get_connection()
    except ConnectionError as e:
        logger.error("Failed to connect to database.", exc_info=e)    
    
    cursor = connection.cursor()
    
    try:
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS %s;" % DATABASE_SETTINGS['NAME']
        )
    except Exception as e:
        logger.error("Schema creation failed.", exc_info=e)
    else:
        logger.info("%s schema creation successful." % DATABASE_SETTINGS['NAME'])
    
    
def make_superuser_admin(*args):
    """
    Makes the 1st superuser an admin.
    """
    from django.contrib.auth.models import Group
    from django.contrib.auth import get_user_model
    User = get_user_model()
    superuser = User.objects.get(username=args[0])
    group, created = Group.objects.get_or_create(name='admin')
    superuser.groups.add(group)
    superuser.save()
    
    
def redirect_cmdline(cmd_name: str):
    """Redirects a command to the right function

    Args:
        cmd_name (str): The name of the command to redirect to
    """
    match cmd_name:
        case 'create_schema' | 'create_database':
            return create_schema
        case 'make_superuser_admin':
            return make_superuser_admin
        case other:
            return lambda:None
        
    
if __name__ == "__main__":
    import sys
    match len(sys.argv):
        case 1:
            create_schema()
        case 2:
            redirect_cmdline(sys.argv[1])(sys.argv[2:])