from django.http import FileResponse
from FlightProject.settings import STATIC_ROOT

def openapi_schema(_):
    response = FileResponse(open(STATIC_ROOT / 'openapi.yaml', 'rb'), content_type='application/yaml')
    response['Content-Disposition'] = 'attachment; filename="openapi.yaml"'
    return response