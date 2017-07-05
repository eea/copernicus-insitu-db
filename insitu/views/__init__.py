from .product_requirement import *
from .product import *
from .requirement import *
from .data_group import *
from .data_responsible import *
from .data_group_data_responsible import *

from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'home.html'
