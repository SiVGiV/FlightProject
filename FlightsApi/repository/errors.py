class RepositoryExceptions(Exception):
    pass

class CreationError(RepositoryExceptions):
    pass

class UpdateError(RepositoryExceptions):
    pass

class FetchError(RepositoryExceptions):
    pass

class DeletionError(RepositoryExceptions):
    pass

class WrongModelType(RepositoryExceptions, TypeError):
    pass