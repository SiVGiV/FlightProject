from functools import wraps
from inspect import getargs
from .exceptions import IncorrectTypePassedToFunctionException
from .general import ordinal

def accepts(*types, throw: Exception = IncorrectTypePassedToFunctionException):
    """
    Adds a layer of type checking to a function.
    Expects as arguments the types of the decorated function's arguments - do not include kwarg types or args with a default value.

    Args:
        *types: The types expected by the function (In identical order)
        throw (Exception, optional): An exception class to raise. Defaults to IncorrectTypePassedToFunction.
    """
    def decorator(func):
        """
        The decorator. This returns the correct wrapper.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            """The wrapped function.

            Raises:
                throw: An exception received from the decorator. Defaults to TypeError.
                ValueError: if an argument is missing
                
            Returns:
                The result of the decorated function.
            """
            # Make sure no arguments are missed because they're passed as kwargs
            # Get expected arguments
            expected_args = getargs(func.__code__)[0]
            # Get expected and actual counts
            expected_arg_count = len(expected_args)
            actual_arg_count = len(args)
            # Make a new list of arguments including any that were missed
            arg_list = [*args]
            for arg_index in range(actual_arg_count, expected_arg_count):
                if expected_args[arg_index] in kwargs:
                    arg_list.append(kwargs[expected_args[arg_index]])
            
            # Compare actual types with expected types
            for type_index in range(len(types)):
                argument_for_check = arg_list[type_index]
                expected_type = types[type_index]
                if not isinstance(argument_for_check, expected_type):
                    if isinstance(expected_type, tuple):
                        expected_name = ' or '.join(map(lambda type: type.__name__, expected_type))
                    else:
                        expected_name = expected_type.__name__
                    raise throw(f"Function '{ func.__name__ }' expected '{ expected_name }' at {ordinal(type_index + 1)} argument but got '{ type(argument_for_check).__name__ }' instead.")
            return func(*args, **kwargs)
        return wrapper
    return decorator
