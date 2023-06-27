from django.views import View
from ..facades import AnonymousFacade

class Countries(View):
    def get(self, request): # /countries
        pass
    
class Country(View):
    def get(self, reqest, id: int): # /country/<id>
        pass