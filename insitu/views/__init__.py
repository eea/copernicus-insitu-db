from .product_requirement import *
from .product import *
from .requirement import *
from .data import *
from .data_provider import *
from .data_provider_relation import *
from .data_requirement import *
from .user import *
from .management import *
from .reports import *
from .crash_me import *

from django.views.generic import TemplateView
from insitu.models import UserLog


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_log = UserLog.objects.filter().order_by('-date')
        user_log = user_log[:10] if len(user_log) >= 10 else user_log
        context['user_log'] = user_log
        return context
