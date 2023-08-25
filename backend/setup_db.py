import os
import django
import logging

# Setup django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FlightProject.settings") 
django.setup()

logger = logging.getLogger('django')
from FlightProject.settings import DATABASES
DATABASE_SETTINGS = DATABASES['default']

def make_superuser_admin(*args):
    """
    Makes the 1st superuser an admin.
    """
    from django.contrib.auth.models import Group
    from FlightsApi.models import Admin
    from django.contrib.auth import get_user_model
    User = get_user_model()
    superuser = User.objects.get(username=os.getenv('DJANGO_SUPERUSER_USERNAME'))
    group, created = Group.objects.get_or_create(name='admin')
    superuser.groups.add(group)
    try:
        admin = Admin.objects.create(
            first_name=os.getenv('DJANGO_SUPERUSER_FIRST_NAME', "Admin"),
            last_name=os.getenv('DJANGO_SUPERUSER_LAST_NAME', ""),
            user=superuser)
    except Exception as e:
        print("Failed to create Admin entry.")
        return
    print(f"Created Superuser: User: {superuser.id}, Admin: {admin.id}")
    
def redirect_cmdline(cmd_name: str):
    """Redirects a command to the right function

    Args:
        cmd_name (str): The name of the command to redirect to
    """
    match cmd_name:
        case 'make_superuser_admin':
            return make_superuser_admin
        case other:
            return lambda:None
        
    
if __name__ == "__main__":
    import sys
    match len(sys.argv):
        case 2:
            redirect_cmdline(sys.argv[1])(sys.argv[2:])