from django.http import HttpResponse
from django.views import View


class Crashme(View):
    def get(self, request):
        if request.user.is_superuser:
            raise RuntimeError("Crashing as requested")
        else:
            return HttpResponse("Must be administrator")
