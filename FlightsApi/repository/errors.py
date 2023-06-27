class RepositoryException(Exception):
    # A Base Exception to be inherited from
    # Always attach exception information to this exception and any exception that inherits from it.
    pass

class CreationError(RepositoryException):
    # An exception to be raised when there was an error creating an object
    pass

class UpdateError(RepositoryException):
    # An exception to be raised when there was an error updating an object
    pass

class FetchError(RepositoryException):
    """
    An exception to be raised when there was an error fetching an object
    """

class DeletionError(RepositoryException):
    """
    An exception to be raised when there was an error deleting an object
    """

class DBExceptions(RepositoryException):
    """
    A Generic Exception class that describes exceptions between the repository and the database
    """

class DBTAbleDoesNotExistException(DBExceptions):
    """
    An exception to raise when attempting to access a non existing table through models or serializers
    """

class NotFoundModelOrSerializerException(DBExceptions):
    """
    An exception to raise when attempting to .get_model() or .get_serializer() but failing
    """

class DBInteractionError(DBExceptions):
    """
    An exception to raise when something went wrong with the query to the DB
    """

class EntityNotFoundException(DBExceptions):
    """
    An exception to raise when attempted to fetch a non existing entity
    """
    
class FailedCreationException(DBExceptions):
    """
    An exception to raise when failed to create an instance in the database
    """
    
class UnacceptableInput(RepositoryException):
    """
    An exception to raise when the input is not acceptable by the method.
    """
    
class OutOfBoundsException(UnacceptableInput):
    """
    An exception to raise when attempting to access the database with data that exceeds the accepted input
    """

class UserAlreadyInGroupException(RepositoryException):
    """
    An exceptions to raise when attempted to add a group to an already assigned user.
    """