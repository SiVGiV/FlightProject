from ..facades import AnonymousFacade, CustomerFacade, AirlineFacade, AdministratorFacade

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class AdminsView(APIView): # /admins
    @permission_classes([IsAuthenticated, ])
    def post(self, request):
        """
        POST /admins - Add a new administrator
        """
        # Get correct facade
        facade, error_msg = AnonymousFacade.login(request)
        if error_msg:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': [error_msg]})
        
        # Check if the user has the right permissions
        if not isinstance(facade, AdministratorFacade):
            return Response(status=status.HTTP_403_FORBIDDEN, data={'errors': ['You do not have the right permissions.']})
        # Get all the details
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        # Call facade and return response
        code, data = facade.add_administrator(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        return Response(status=code, data=data)
    
class AdminView(APIView): # /admin/<id>
    def delete(self, request, id: int):
        """
        DELETE /admin/<int:id> - Deactivate an administrator
        """
        # Get correct facade
        facade, error_msg = AnonymousFacade.login(request)
        if error_msg:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': [error_msg]})
        
        # Check if the user has the right permissions
        if not isinstance(facade, AdministratorFacade):
            return Response(status=status.HTTP_403_FORBIDDEN, data={'errors': ['You do not have the right permissions.']})
        
        # Call facade and return response
        code, data = facade.deactivate_administrator(id)
        return Response(status=code, data=data)