import os
import django


# Setup django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FlightProject.settings") 
django.setup()

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
    return connection


def create_schema():
    """Creates the main django schema
    """
    from FlightProject.settings import DATABASES
    
    DATABASE_SETTINGS = DATABASES['default']
    
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "CREATE DATABASE IF NOT EXISTS %s;" % DATABASE_SETTINGS['NAME']
    )
    
    
def redirect_cmdline(cmd_name: str):
    """Redirects a command to the right function

    Args:
        cmd_name (str): The name of the command to redirect to
    """
    match cmd_name:
        case 'create_schema' | 'create_database':
            return create_schema
        case other:
            return lambda:None
    
if __name__ == "__main__":
    import sys
    match len(sys.argv):
        case 1:
            create_schema()
        case 2:
            redirect_cmdline(sys.argv[1])()
        case other:
            pass