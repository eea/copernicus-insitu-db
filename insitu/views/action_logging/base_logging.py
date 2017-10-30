import csv
import json

from copernicus.settings import LOGGING_CSV_FILENAME
from datetime import datetime


class BaseLoggingView:

    target_type = ''
    extra = ''

    def get_object_id(self):
        return ''

    def log_action(self, request, action, id=''):
        with open(LOGGING_CSV_FILENAME, 'a') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',')
            row = ",".join([
                datetime.now().strftime('%d %B %Y %H:%M'),
                request.user.username,
                action,
                self.target_type,
                str(id),
                self.extra
            ])
            spamwriter.writerow(row.split(','))


class GetMethodLoggingView(BaseLoggingView):
    get_action = None

    def get(self, request, *args, **kwargs):
        id = self.get_object_id()
        self.log_action(request, self.get_action, id)
        return super().get(request, *args, **kwargs)


class PostMethodLoggingView(BaseLoggingView):
    post_action = None

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        self.extra = json.dumps(self.get_form().errors)
        if self.extra:
            self.post_action = 'tried to create'
        id = self.get_object_id()
        self.log_action(request, self.post_action, id)
        return response


class PutMethodLoggingView(BaseLoggingView):
    post_action = None

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        id = self.get_object_id()
        self.log_action(request, self.post_action, id)
        return response


class DeleteMethodLoggingView(BaseLoggingView):
    post_action = None

    def post(self, request, *args, **kwargs):
        id = self.get_object_id()
        response = super().post(request, *args, **kwargs)
        self.log_action(request, self.post_action, id)
        return response


class CreateLoggingView(GetMethodLoggingView, PostMethodLoggingView):
    get_action = 'visited create page of'
    post_action = 'created'

    def get_object_id(self):
        if hasattr(self, 'object') and self.object:
            return self.object.id
        return ''

    def form_invalid(self, form):
        response = super().form_invalid(form)
        self.extra = ",".join(
            [value[0] for key, value in form.errors.items()])
        if self.extra:
            self.post_action = 'tried to create'
        return response


class UpdateLoggingView(GetMethodLoggingView, PutMethodLoggingView):
    get_action = 'visited edit page of'
    post_action = 'updated'

    def get_object_id(self):
        return self.get_object().id

    def form_invalid(self, form):
        response = super().form_invalid(form)
        self.extra = ",".join(
            [value[0] for key, value in form.errors.items()])
        if self.extra:
            self.post_action = 'tried to update'
        return response


class DeleteLoggingView(GetMethodLoggingView, DeleteMethodLoggingView):
    get_action = 'visited delete page of'
    post_action = 'deleted'

    def get_object_id(self):
        return self.get_object().id


class ListLoggingView(GetMethodLoggingView):
    get_action = 'visited list page of'


class DetailLoggingView(GetMethodLoggingView):
    get_action = 'visited detail page of'

    def get_object_id(self):
        return self.get_object().id