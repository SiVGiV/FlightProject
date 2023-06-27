class FacadeException(Exception):
    """
    
    """

class RepositoryTransactionException(FacadeException):
    """
    An exception that occurs in the interaction with the database.
    """