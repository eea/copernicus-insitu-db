from django_datatables_view.base_datatable_view import BaseDatatableView

from insitu.utils import ALL_OPTIONS_LABEL


class ESDatatableView(BaseDatatableView):
    def get_initial_queryset(self):
        return self.document.search()

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
