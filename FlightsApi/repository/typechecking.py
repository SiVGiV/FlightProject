from django.db.models import Model
from functools import wraps
from inspect import isclass, getargs
from .errors import WrongModelType

def verify_model(func):
    """A decorator to verify that the 1st argument passed to a function is of type Model

    Args:
        func (func): A function to decorate
        
    Raises:
        WrongModelType for types that aren't Model
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get the model object from the function's arguments
        modelObj = args[0]
        
        # check if the modelObj is a class: necessary before checking issubclass()
        if not isclass(modelObj): 
            raise WrongModelType("model must be of type Model")
        
        # Check if the modelObj is a subclass of Model
        if not issubclass(modelObj, Model): 
            raise WrongModelType("model must be of type Model")
        # Run the decorated function
        return func(*args, **kwargs)
    return wrapper

def accepts(*types, throw: Exception = TypeError, model: bool = False):
    """Catches the arguments passed to the decorator (not the actual function that runs around the decorated function)

    Args:
        throw (Exception, optional): An exception class to raise. Defaults to TypeError.
        model (bool, optional): True if decorated function takes model as 1st argument. Defaults to False.
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

            Returns:
                The result of the decorated function.
            """
            # This bit of code makes sure no arguments are missed because they're passed as kwargs
            # Get expected arguments
            expected_args = getargs(func.__code__)[0]
            # Get expected and actual counts
            expected_arg_count = len(expected_args)
            actual_arg_count = len(args)
            # Make a new list of arguments including any that were missed
            arg_list = [*args]
            for arg_index in range(actual_arg_count, expected_arg_count):
                arg_list.append(kwargs[expected_args[arg_index]])
            
            skip_model = 1 if model else 0
            # Compare actual types with expected types
            for type_index in range(skip_model, expected_arg_count):
                argument_index = type_index
                argument_for_check = arg_list[argument_index]
                expected_type = types[type_index - skip_model]
                
                if not isinstance(argument_for_check, expected_type):
                    raise throw(f"{ func.__name__ } expected { expected_type.__name__ } at {ordinal(argument_index)} argument but got { type(argument_for_check).__name__ } instead.")
            return func(*args, **kwargs)

        # Perform model verification if model is True
        if model:
            return verify_model(wrapper)
        else:
            return wrapper
    return decorator
