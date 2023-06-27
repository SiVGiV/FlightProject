from django.http import JsonResponse
from rest_framework.status import is_success

class FacadeResponse():
    def __init__(self, status: int, data: dict = None, errors: list = None, **additional_fields):
        self.__body = { 'status': status }
        if is_success(status):
            if data is None:
                raise ValueError('Status code implies successful but no data was given.')
            self.__body['data'] = data
        else:
            if errors is None:
                raise ValueError('Status code implies errors but none were given.')
            self.__body['errors'] = errors
        self.__body.update(additional_fields)
            
    @property
    def dict(self):
        return self.__body
    
    def renderJSON(self):
        return JsonResponse(self.dict)