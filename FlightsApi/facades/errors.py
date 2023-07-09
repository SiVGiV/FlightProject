class FacadeException(Exception):
    """
    An exception base class to be inherited from
    """

class RepositoryTransactionException(FacadeException):
    """
    An exception that occurs in the interaction with the database.
    """