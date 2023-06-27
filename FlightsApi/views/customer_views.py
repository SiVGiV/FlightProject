from django.views import View
from ..facades import AnonymousFacade, CustomerFacade, AirlineFacade, AdministratorFacade
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

import logging
logger = logging.getLogger(__name__)

class Customers(APIView): # /customers
    permission_classes = [IsAuthenticated,]
    def get(self, request):
        # Get correct facade
        facade, error_msg = AnonymousFacade.login(request)
        if error_msg:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': [error_msg]})
        
        # Check if the user has the right permissions
        if not isinstance(facade, AdministratorFacade):
            return Response(status=status.HTTP_403_FORBIDDEN, data={'errors': ['You do not have the right permissions.']})
        
        # Validate pagination inputs
        try:
            limit = int(request.GET.get('limit', 0))
            page = int(request.GET.get('limit', 0))
        except ValueError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': ['Pagination limit or page are not integers.']})
        
        code, data = facade.get_all_customers(request, limit=limit or 0, page=page or 0)
        return Response(status=code, data=data)
        
    
    def post(self, request):
        pass
    
    def put(self, request):
        pass
    
    def patch(self, request):
        pass
    
class Customer(View): # /customer/<id>
    permission_classes = [IsAuthenticated,]
    def get(self, request):
        pass
    
    def post(self, request):
        pass
    
    def put(self, request):
        pass
    
    def patch(self, request):
        pass
    
    def delete(self, request):
        pass