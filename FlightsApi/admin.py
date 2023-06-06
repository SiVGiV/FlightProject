from django.contrib import admin

from .models import *

admin.site.register(Country)
admin.site.register(UserRole)
admin.site.register(User)
admin.site.register(Admin)
admin.site.register(AirlineCompany)
admin.site.register(Customer)
admin.site.register(Flight)
admin.site.register(Ticket)
