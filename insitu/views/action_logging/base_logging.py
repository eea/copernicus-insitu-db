import csv
import json
import sys
from datetime import datetime


class BaseLoggingView:

    target_type = ''
    extra = ''

    def get_object_id(self):
        return ''

    def log_action(self, request, action, id=''):
        if 'test' in sys.argv:
            from copernicus.testsettings import LOGGING_CSV_FILENAME
        else:
            from copernicus.settings import LOGGING_CSV_FILENAME
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
        errors = self.get_form().errors
        action = self.post_action
        if errors:
            self.extra = json.dumps(errors)
            action = self.post_action_failed
        id = self.get_object_id()
        self.log_action(request, action, id)
        return response


class PutMethodLoggingView(BaseLoggingView):
    post_action = None

    def post(self, request, *args, **kwargs):
        errors = self.get_form().errors
        response = super().post(request, *args, **kwargs)
        action = self.post_action
        if errors:
            self.extra = json.dumps(errors)
            action = self.post_action_failed
        id = self.get_object_id()
        self.log_action(request, action, id)
        return response


class DeleteMethodLoggingView(BaseLoggingView):
    post_action = None

    def post(self, request, *args, **kwargs):
        id = self.get_object_id()
        response = super().post(request, *args, **kwargs)
        action = self.post_action
        self.log_action(request, action, id)
        return response


class CreateLoggingView(GetMethodLoggingView, PostMethodLoggingView):
    get_action = 'visited create page of'
    post_action = 'created'
    post_action_failed = 'tried to create'

    def get_object_id(self):
        if hasattr(self, 'object') and self.object:
            return self.object.id
        return ''


class UpdateLoggingView(GetMethodLoggingView, PutMethodLoggingView):
    get_action = 'visited edit page of'
    post_action = 'updated'
    post_action_failed = 'tried to update'

    def get_object_id(self):
        return self.get_object().id


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
