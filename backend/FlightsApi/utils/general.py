from functools import wraps
from ..models import User
from logging import getLogger
from inspect import stack
import re

logger = getLogger('django')

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
        logger.debug(f"Called {func.__name__}")
        res = func(*args, **kwargs)
        logger.debug(f"{func.__name__} finished")
        return res
    return wrapper

def is_admin(user: User):
    return user.groups.filter(name='admin').exists()

def is_customer(user: User):
    return user.groups.filter(name='customer').exists()

def is_airline(user: User):
    return user.groups.filter(name='airline').exists()



class StringValidation:
    @staticmethod
    def is_natural_int(s: str):
        """Checks if a string is a natural number

        Args:
            s (str): A string to check

        Returns:
            bool: True if the string is a natural number, False otherwise
        """
        try:
            return bool(re.match(r"^[0]*[1-9]\d*$", s))
        except ValueError:
            return False
        
    @staticmethod
    def is_valid_password(s: str):
        """Checks if a string is a valid password
        
        Args:
            s (str): A string to check
            
        Returns:
            bool: True if the string is a valid password, False otherwise
        """
        
        # use regex to check if the password contains at least 1 uppercase letter, 1 lowercase letter, 1 number, and 1 special character
        return bool(re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]", s)) and len(s) >= 8
        #                       ^^^^^^      ^^^^^^     ^^^^^^      ^^^^^^
        #                       [lower]     [upper]    [number]    [special character]
        
        
    @staticmethod
    def is_valid_email(s: str):
        """Checks if a string is a valid email address

        Args:
            s (str): A string to check
            
        Returns:
            bool: True if the string is a valid email address, False otherwise
        """
        # use regex to check if the email address is valid
        return bool(re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", s))
    
    @staticmethod
    def is_valid_phone_number(s: str):
        """Checks if a string is a valid phone number

        Args:
            s (str): A string to check
            
        Returns:
            bool: True if the string is a valid phone number, False otherwise
        """
        # use regex to check if the phone number is valid
        return bool(re.match(r"^(?:(?:(\+?972|\(\+?972\)|\+?\(972\))(?:\s|\.|-)?([1-9]\d?))|(0[23489]{1})|(0[57]{1}[0-9]))(?:\s|\.|-)?([^0\D]{1}\d{2}(?:\s|\.|-)?\d{4})$", s))