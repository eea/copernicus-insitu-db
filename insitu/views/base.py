from django.views.generic.edit import ModelFormMixin
from django_datatables_view.base_datatable_view import BaseDatatableView
from elasticsearch_dsl import Q

from insitu.utils import ALL_OPTIONS_LABEL
from insitu.views.protected.views import ProtectedView


class ESDatatableView(BaseDatatableView, ProtectedView):
    def get_initial_queryset(self):
        return self.document.search()

    def ordering(self, qs):
        search_text = self.request.GET.get('search[value]', '')
        if search_text:
            return qs
        return super().ordering(qs)

    def filter_queryset(self, qs):
        for filter in self.filters:
            value = self.request.GET.get(filter)
            if not value or value == ALL_OPTIONS_LABEL:
                continue
            qs = qs.filter('term', **{filter: value})

        search_text = self.request.GET.get('search[value]', '')
        if not search_text:
            return qs
        return qs.query('query_string', query=search_text)


class CreatedByMixin:
    def form_valid(self, form):
        self.object = form.save(created_by=self.request.user)
        return super(ModelFormMixin, self).form_valid(form)
