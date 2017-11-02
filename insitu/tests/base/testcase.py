from django.test import TestCase

from insitu.tests.base import UserFactory


class FormCheckTestCase(TestCase):
    fields = []
    related_fields = []
    many_to_many_fields = []
    required_fields = []
    related_entities_updated = []
    related_entities_fields = []
    REQUIRED_ERROR = ['This field is required.']

    def setUp(self):
        self.errors = {field: self.REQUIRED_ERROR for field in self.required_fields}
        self.creator = UserFactory(username='Creator')
        self.other_user = UserFactory(username='Other')

    def login_creator(self):
        self.client.force_login(self.creator)

    def check_required_errors(self, resp, errors):
        self.assertEqual(resp.status_code, 200)
        self.assertIsNot(resp.context['form'].errors, {})
        self.assertDictEqual(resp.context['form'].errors, errors)

    def check_object(self, object, data):
        for field in self.fields:
            self.assertEqual(getattr(object, field), data[field], field)
        for related_field in self.related_fields:
            self.assertEqual(getattr(object, related_field).pk,
                             data[related_field], related_field)
        for many_to_many_field in self.many_to_many_fields:
            manager = getattr(object, many_to_many_field)
            self.assertEqual(manager.count(), len(data[many_to_many_field]),
                             many_to_many_field)
            for related_instance in manager.all():
                self.assertTrue(related_instance.pk in data[many_to_many_field],
                                many_to_many_field)
        for entity in self.related_entities_updated:
            for field in self.related_entities_fields:
                self.assertEqual(
                    getattr(getattr(object, entity), field),
                    data["_".join([entity, field])],
                    entity + "-" + field)

    def check_single_object(self, model_cls, data):
        qs = model_cls.objects.all()
        self.assertEqual(qs.count(), 1)
        object = qs.first()
        self.check_object(object, data)

    def check_single_object_deleted(self, model_cls):
        self.assertFalse(model_cls.objects.exists())

    def check_objects_are_soft_deleted(self, model_cls, document=None):
        self.assertTrue(model_cls.objects.really_all())
        for obj in model_cls.objects.really_all():
            self.assertTrue(obj._deleted)
            if document:
                resp = document.get(id=obj.id, ignore=404)
                self.assertIsNone(resp)


class PermissionsCheckTestCase(TestCase):

    def setUp(self):
        self.creator = UserFactory(is_superuser=True,
                                   username='Creator')

    def _login_user(self):
        user = UserFactory()
        self.client.force_login(user)

    def check_permission_denied(self, method, url):
        resp = None
        if method == 'GET':
            resp = self.client.get(url)
        elif method == 'POST':
            resp = self.client.post(url)
        self.assertEqual(resp.status_code, 403)

    def check_permission_all_methods_denied(self, url):
        for method in ['GET', 'POST']:
            self.check_permission_denied(method, url)

    def check_user_redirect(self, method, url, redirect_url):
        resp = None
        if method == 'GET':
            resp = self.client.get(url, follow=True)
        elif method == 'POST':
            resp = self.client.post(url, follow=True)
        self.assertRedirects(resp, redirect_url)

    def check_authenticated_user_redirect(self, method, url, redirect_url):
        self._login_user()
        self.check_user_redirect(method, url, redirect_url)
        self.client.logout()

    def check_user_redirect_all_methods(self, url, redirect_url):
        for method in ['GET', 'POST']:
            self.check_user_redirect(method, url, redirect_url)

    def check_authenticated_user_redirect_all_methods(self, url, redirect_url):
        self._login_user()
        for method in ['GET', 'POST']:
            self.check_user_redirect(method, url, redirect_url)
        self.client.logout()
