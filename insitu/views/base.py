from django.conf import settings
from django.core.mail import send_mail
from django.views.generic.edit import ModelFormMixin
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.template.loader import render_to_string

from copernicus.settings import DEFAULT_FROM_EMAIL, SITE_URL
from insitu.utils import ALL_OPTIONS_LABEL
from insitu.views.protected.views import ProtectedView


class ESDatatableView(BaseDatatableView, ProtectedView):
    filter_translation = {}
    extra_filters = {}
    escape_values = False

    def get_initial_queryset(self):
        return self.document.search()

    def ordering(self, qs):
        sorting_cols = 0
        if self.pre_camel_case_notation:
            try:
                sorting_cols = int(self._querydict.get("iSortingCols", 0))
            except ValueError:
                sorting_cols = 0
        else:
            sort_key = "order[{0}][column]".format(sorting_cols)
            while sort_key in self._querydict:
                sorting_cols += 1
                sort_key = "order[{0}][column]".format(sorting_cols)

        order = []
        order_columns = self.get_order_columns()
        for i in range(sorting_cols):
            # sorting column
            sort_dir = "asc"
            try:
                if self.pre_camel_case_notation:
                    sort_col = int(self._querydict.get("iSortCol_{0}".format(i)))
                    # sorting order
                    sort_dir = self._querydict.get("sSortDir_{0}".format(i))
                else:
                    sort_col = int(self._querydict.get("order[{0}][column]".format(i)))
                    # sorting order
                    sort_dir = self._querydict.get("order[{0}][dir]".format(i))
            except ValueError:
                sort_col = 0

            sdir = "-" if sort_dir == "desc" else ""
            sortcol = order_columns[sort_col]

            if isinstance(sortcol, list):
                for sc in sortcol:
                    order.append("{0}{1}".format(sdir, sc.replace(".", "__")))
            else:
                order.append("{0}{1}".format(sdir, sortcol.replace(".", "__")))

        if order:
            for i in range(0, len(order)):
                if order[i] == "name":
                    order[i] = "name.raw"
                if order[i] == "-name":
                    order[i] = "-name.raw"
            return qs.order_by(*order)
        return qs

    def filter_queryset(self, search):
        """
        Where `search` is a django_elasticsearch_dsl.search.Search object.

        TODO: Investigate the possibility of only using ElasticSearch for text
        searches.
        """
        for filter_ in self.filters:
            value = self.request.GET.get(filter_)
            if not value or value == ALL_OPTIONS_LABEL:
                continue
            if filter_ in self.filter_translation.keys():
                filter_ = self.filter_translation[filter_]
            search = search.query("term", **{filter_: value})

        search_text = self.request.GET.get("search[value]", "")
        if search_text:
            search = search.query(
                "query_string", default_field="name", query='"' + search_text + '"'
            )

        if search.count() > settings.MAX_RESULT_WINDOW or not hasattr(
            self, "filter_fields"
        ):
            # If there are more than MAX_RESULT_WINDOW matching objects in the
            # database, don't bother syncing the filter options. It would be too
            # complicated and costly.
            return search

        search = search[0 : settings.MAX_RESULT_WINDOW]

        qs = search.to_queryset()  # If there are ever more than 10,000
        # items in the database, this will have to be reimplemented entirely.
        qs = qs.filter(**self.extra_filters)

        objects = qs.values_list(*self.filter_fields)

        self._filter_options = dict(
            [
                (
                    filter_,
                    {"options": options, "selected": self.request.GET.get(filter_)},
                )
                for filter_, options in zip(
                    self.filters,
                    [
                        sorted([opt for opt in set(options) if opt not in ["", None]])
                        for options in zip(*objects)
                    ],
                )
            ]
        )
        return search

    def get_context_data(self, *args, **kwargs):
        ret = super().get_context_data(*args, **kwargs)
        if hasattr(self, "_filter_options"):
            ret.update({"filters": self._filter_options})
        return ret


class CreatedByMixin:
    def form_valid(self, form):
        self.object = form.save(created_by=self.request.user)
        return super(ModelFormMixin, self).form_valid(form)


class ChangesRequestedMailMixin:
    transition_name = "request_changes"

    def send_mail(self, target_object, feedback=""):
        sender = self.request.user
        receiver = target_object.created_by
        subject = 'Changes requested for "{}" {}'.format(
            target_object.name,
            self.target_type,
        )
        context = {
            "target": self.target_type,
            "feedback": feedback,
            "receiver": receiver,
            "sender": sender,
            "object": target_object,
            "url": SITE_URL + self.get_success_url(),
        }
        html_message = render_to_string("mails/request_changes.html", context=context)
        message = render_to_string("mails/request_changes.txt", context=context)
        send_mail(
            subject=subject,
            message=message,
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=[receiver.email],
            html_message=html_message,
        )
