import logging
from functools import wraps
from ..models import User
logger = logging.getLogger(__name__)

def ordinal(n: int):
    """Converts an int to an ordinal number (1 -> 1st, 2 -> 2nd, ...)

    Args:
        n (int): A natural number

    Returns:
        str: An ordinal number string
    """
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix


def log_action(func):
    """Logs function calls at the debug level

    Args:
        func (function): A function to decorate
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Called {func.__name__} @ {__name__}")
        res = func(*args, **kwargs)
        logger.debug(f"{func.__name__} finished @ {__name__}")
        return res
    return wrapper

def is_admin(user: User):
    return user.groups.filter(name='admin').exists()

def is_customer(user: User):
    return user.groups.filter(name='customer').exists()

def is_airline(user: User):
    return user.groups.filter(name='airline').exists()