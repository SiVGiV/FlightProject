from ..forms import UserRegisterForm
from django.views.generic.edit import CreateView

# Create your views here.
class RegisterView(CreateView):
    template_name = "register.html"
    form_class = UserRegisterForm
