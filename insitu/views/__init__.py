from .product_requirement import *
from .product import *
from .requirement import *
from .data import *
from .data_provider import *
from .data_provider_relation import *
from .data_requirement import *
from .user import *
from .management import *

from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'home.html'
