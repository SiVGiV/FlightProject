class Paginate():
    """
    A 1 indexed pagination class.
    """
    def __init__(self, per_page: int = 0, page_number: int = 0):
        """
        Create a Paginate object. If any of the arguments is zero or below, doesn't paginate.

        Args:
            per_page (int, optional): Number of items per page. Defaults to 0.
            page_number (int, optional): Page number. Defaults to 0.
        """
        self.__per_page = per_page if per_page > 0 else 0
        self.__page_number = page_number if page_number > 0 else 0
        
    @property
    def slice(self):
        """
        Creates a slice based on the pagination parameters.

        Returns:
            Type[slice]: A slice objects with the pagination parameters.
        """
        if self.__per_page == 0 or self.__page_number == 0:
            return slice(None, None)
        start = (self.__page_number - 1) * self.__per_page
        stop = self.__page_number * self.__per_page
        return slice(start, stop)
    
    def __getitem__(self, key):
        if key == "page":
            return self.__page_number
        elif key == "limit":
            return self.__per_page
        
    def keys(self):
        return ('page', 'limit')