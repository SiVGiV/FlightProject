class RepositoryExceptions(Exception):
    # A Base Exception to be inherited from
    # Always attach exception information to this exception and any exception that inherits from it.
    pass

class CreationError(RepositoryExceptions):
    # An exception to be raised when there was an error creating an object
    pass

class UpdateError(RepositoryExceptions):
    # An exception to be raised when there was an error updating an object
    pass

class FetchError(RepositoryExceptions):
    # An exception to be raised when there was an error fetching an object
    pass

class DeletionError(RepositoryExceptions):
    # An exception to be raised when there was an error deleting an object
    pass

class WrongModelType(RepositoryExceptions, TypeError):
    pass