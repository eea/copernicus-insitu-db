import csv
import json
import sys
from datetime import datetime
from insitu.models import UserLog


class BaseLoggingView:

    target_type = ''
    extra = ''

    def get_object_id(self):
        return ''

    def log_action(self, request, action, id=''):
        if 'test' in sys.argv:
            from copernicus.test_settings import LOGGING_CSV_FILENAME, LOGGING_CSV_PATH
        else:
            from copernicus.settings import LOGGING_CSV_FILENAME, LOGGING_CSV_PATH
        with open(LOGGING_CSV_PATH, 'a+') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',')
            row = ",".join([
                datetime.now().strftime('%d %B %Y %H:%M'),
                request.user.username,
                action,
                self.target_type,
                str(id),
                self.extra
            ]).strip(",")
            spamwriter.writerow(row.split(','))

        BaseLoggingView.add_user_log(request.user, action, id, self.target_type)

    @staticmethod
    def add_user_log(user, action, id, target_type):
        text = " ".join([
                action,
                target_type,
                str(id)
            ]).strip(" ")
        log = {
            'text': text,
            'date': datetime.now(),
            'user': user
        }
        UserLog.objects.create(**log)


class GetMethodLoggingView(BaseLoggingView):
    get_action = None

    def get(self, request, *args, **kwargs):
        id = self.get_object_id()
        self.log_action(request, self.get_action, id)
        return super().get(request, *args, **kwargs)


class PostMethodLoggingView(BaseLoggingView):
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


class PutMethodLoggingView(BaseLoggingView):
    post_action = None

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        try:
            self.instance = self.get_object()
            form.instance = self.instance
            errors = form.errors
        except:
            errors = form.errors
        response = super().post(request, *args, **kwargs)
        action = self.post_action
        if errors and response.status_code != 302:
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


class CreateLoggingView(PostMethodLoggingView):
    post_action = 'created'
    post_action_failed = 'tried to create'

    def get_object_id(self):
        if hasattr(self, 'object') and self.object:
            return self.object.id
        return ''


class UpdateLoggingView(PutMethodLoggingView):
    post_action = 'updated'
    post_action_failed = 'tried to update'

    def get_object_id(self):
        return self.get_object().id


class DeleteLoggingView(DeleteMethodLoggingView):
    post_action = 'deleted'

    def get_object_id(self):
        return self.get_object().id


class ListLoggingView(GetMethodLoggingView):
    get_action = 'visited list page of'


class DetailLoggingView(GetMethodLoggingView):
    get_action = 'visited detail page of'

    def get_object_id(self):
        return self.get_object().id


class TrasitionLoggingView(PostMethodLoggingView):
    get_action = 'visited transition page of '

    def get_object_id(self):
        return self.get_object().id
