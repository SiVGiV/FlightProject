from django.contrib.auth import logout
from rest_framework.response import Response
from FlightsApi.utils.response_utils import no_content_ok

def logout(request):
    logout(request)
    request.COOKIES['usertype'] = 'anon'
    code, res = no_content_ok()
    return Response(status=code, data=res)