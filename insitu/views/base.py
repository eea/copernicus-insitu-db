from django.views.generic.edit import ModelFormMixin
from django_datatables_view.base_datatable_view import BaseDatatableView
from elasticsearch_dsl import analyzer
from elasticsearch_dsl import tokenizer

from insitu.utils import ALL_OPTIONS_LABEL
from insitu.views.protected.views import ProtectedView


class ESDatatableView(BaseDatatableView, ProtectedView):
    def get_initial_queryset(self):
        return self.document.search()

    def ordering(self, qs):
        sorting_cols = 0
        if self.pre_camel_case_notation:
            try:
                sorting_cols = int(self._querydict.get('iSortingCols', 0))
            except ValueError:
                sorting_cols = 0
        else:
            sort_key = 'order[{0}][column]'.format(sorting_cols)
            while sort_key in self._querydict:
                sorting_cols += 1
                sort_key = 'order[{0}][column]'.format(sorting_cols)

        order = []
        order_columns = self.get_order_columns()
        for i in range(sorting_cols):
            # sorting column
            sort_dir = 'asc'
            try:
                if self.pre_camel_case_notation:
                    sort_col = int(self._querydict.get('iSortCol_{0}'.format(i)))
                    # sorting order
                    sort_dir = self._querydict.get('sSortDir_{0}'.format(i))
                else:
                    sort_col = int(self._querydict.get('order[{0}][column]'.format(i)))
                    # sorting order
                    sort_dir = self._querydict.get('order[{0}][dir]'.format(i))
            except ValueError:
                sort_col = 0

            sdir = '-' if sort_dir == 'desc' else ''
            sortcol = order_columns[sort_col]

            if isinstance(sortcol, list):
                for sc in sortcol:
                    order.append('{0}{1}'.format(sdir, sc.replace('.', '__')))
            else:
                order.append('{0}{1}'.format(sdir, sortcol.replace('.', '__')))

        if order:
            for i in range(0, len(order)):
                if order[i] == 'name':
                    order[i] = 'name.raw'
                if order[i] == '-name':
                    order[i] = '-name.raw'
            return qs.order_by(*order)
        return qs

    def filter_queryset(self, qs):
        for filter in self.filters:
            value = self.request.GET.get(filter)
            if not value or value == ALL_OPTIONS_LABEL:
                continue
            qs = qs.filter('term', **{filter: value})

        search_text = self.request.GET.get('search[value]', '')
        if not search_text:
            return qs
        return qs.query('query_string', default_field='name',
                        query='"' + search_text + '"')


class CreatedByMixin:
    def form_valid(self, form):
        self.object = form.save(created_by=self.request.user)
        return super(ModelFormMixin, self).form_valid(form)
