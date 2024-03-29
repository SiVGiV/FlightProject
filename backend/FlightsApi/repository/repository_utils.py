class Paginate():
    """
    A 1 indexed pagination class.
    """
    def __init__(self, per_page: int = 50, page_number: int = 1, total: int = 0):
        """
        Create a Paginate object. If any of the arguments is zero or below, doesn't paginate.

        Args:
            per_page (int, optional): Number of items per page. Defaults to 50.
            page_number (int, optional): Page number. Defaults to 1.
        """
        self.__per_page = per_page if per_page > 0 else 50
        self.__page_number = page_number if page_number > 0 else 1
        self.__total = total if total >= 0 else 0
        
    @property
    def total(self):
        return self.__total
        
    @total.setter
    def total(self, value):
        if value >= 0:
            self.__total = value
        else:
            raise ValueError("Pagination total cannot be lower than 0.")
    
    @property
    def slice(self):
        """
        Creates a slice based on the pagination parameters.

        Returns:
            Type[slice]: A slice objects with the pagination parameters.
        """
        # Return a nully slice if one of the values is zero.
        if self.__per_page == 0 or self.__page_number == 0:
            return slice(None, None)
        start = (self.__page_number - 1) * self.__per_page
        stop = self.__page_number * self.__per_page
        return slice(start, stop)
    
    # The combination of __getitem__() and keys() in an object allows for unpacking as a dictionary (ie. { **Paginate() } )
    def __getitem__(self, key):
        if key == "page":
            return self.__page_number
        elif key == "limit":
            return self.__per_page
        
    def keys(self):
        return ('page', 'limit', 'total')
    
    def get_dict(self):
        return {'limit': self.__per_page, 'page': self.__page_number, 'total': self.__total}