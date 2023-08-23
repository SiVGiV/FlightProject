"""
URL configuration for FlightProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .views import openapi_schema
from drf_spectacular.views import SpectacularSwaggerView

urlpatterns = [
    path('api/', include('FlightsApi.urls')),
    path('admin/', admin.site.urls),
    path('schema/', csrf_exempt(openapi_schema), name='openapi-schema'),
    path('swagger/', csrf_exempt(SpectacularSwaggerView.as_view(url_name='openapi-schema')), name='swagger'),
    path('healthcheck/', csrf_exempt(lambda r: HttpResponse(status=204))),
]