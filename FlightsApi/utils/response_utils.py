from rest_framework import status
from django.core.exceptions import ValidationError
from ..repository.errors import EntityNotFoundException, UserAlreadyInGroupException, OutOfBoundsException, FetchError
from logging import getLogger

logger = getLogger('django')


def not_found_response(errors=None):
    return create_facade_response(status.HTTP_404_NOT_FOUND, errors=errors)

def internal_error_response(errors=None):
    return create_facade_response(status.HTTP_500_INTERNAL_SERVER_ERROR, errors=errors)

def bad_request_response(errors=None):
    return create_facade_response(status.HTTP_400_BAD_REQUEST, errors=errors)

def conflict_response(errors=None):
    return create_facade_response(status.HTTP_409_CONFLICT, errors=errors)

def forbidden_response():
    error_msg = 'You do not own this entity and cannot make changes to it.'
    return create_facade_response(status.HTTP_403_FORBIDDEN, errors=error_msg)

def ok_response(data=None, pagination=None):
    return create_facade_response(status.HTTP_200_OK, data=data, pagination=pagination)

def created_response(data=None):
    return create_facade_response(status.HTTP_201_CREATED, data=data)

def no_content_ok():
    return create_facade_response(status.HTTP_204_NO_CONTENT)

def create_facade_response(code, data = None, errors = None, pagination = None):
    logger.debug(f"{code}: {data = } ||| {errors = }")
    if status.is_server_error(code):
        added_str = ''
        if errors:
            added_str += '\n\n'
            if isinstance(errors, Exception):
                added_str += str(errors)
            elif isinstance(errors, str):
                added_str += errors
        return code, dict_builder(errors='The server encountered an unexpected error.' + added_str)
    elif not status.is_success(code):
        return code, dict_builder(errors=errors)
    elif code == status.HTTP_204_NO_CONTENT:
        return code, None
    else:
        return code, dict_builder(data=data, pagination=pagination)

def stringify_exception(exception):
    res = ''
    if isinstance(exception, (ValueError, TypeError, ValidationError)):
        res += 'One or more of the passed values caused an error\n.'
        res += 'Check your parameters and try again.\n'
    elif isinstance(exception, EntityNotFoundException):
        res += 'The entity you are trying to access was not found.\n'
        res += 'Make sure the ID is correct and that the entity indeed exists.\n'
    elif isinstance(exception, UserAlreadyInGroupException):
        res += 'The user you are trying to create/modify is already in a group and cannot be added to another one.\n'
        res += 'Try creating a new user or remove the user from all groups before trying again.\n'
    elif isinstance(exception, OutOfBoundsException):
        res += 'The provided entity ID exceeds the permitted boundaries.\n'
        res += 'Check that the ID is larger than 0 and try again.\n'
    elif isinstance(exception, FetchError):
        res += 'Could not fetch this entity for updating.\n'
        res += 'Check that this entity exists and that your parameters are correct and try again.\n'
    else:
        res += 'The server encountered an unexpected error.\n'

    res += str(exception)
    return res

def dict_builder(**fields):
    result = {}
    for key, value in fields.items():
        if not value: # Skip empty values - None, [], {}, ""
            continue
        match key:
            # Errors must not exist alongside other top-level keys
            # so we return them instantly
            case 'errors':
                if isinstance(value, str):
                    return {'error': value}
                elif (isinstance(value, list) and len(value) == 1):
                    return {'error': value[0]}
                elif (isinstance(value, dict) and len(value.keys()) == 1):
                    return {'error': value}
                elif (isinstance(value, Exception)):
                    logger.error(value)
                    return {'error': stringify_exception(value)}
                else:
                    return {'errors': value}
            
            case 'data':
                result.update({'data': value})
                
            case 'pagination':
                result.update({'pagination': value.get_dict()})
    return result 