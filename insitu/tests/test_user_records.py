from django.urls import reverse
from insitu.tests import base
from insitu import models


class UserRecordsTests(base.FormCheckTestCase):
    def test_user_records(self):
        self.login_creator()
        user_data = base.DataFactory(created_by=self.creator)
        user_provider = base.DataProviderFactory(created_by=self.creator)
        user_provider_rel = base.DataProviderRelationFactory(
            created_by=self.creator,
            data=user_data,
            provider=user_provider,
        )
        link_table_name = "Links between Data and Data Providers"

        resp = self.client.get(reverse("user_records"))

        self.assertEqual(resp.status_code, 200)

        expected_response_queryset = models.Data.objects.filter(id=user_data.id)
        self.assertQuerySetEqual(resp.context["data_list"], expected_response_queryset)
        self.assertEqual(resp.context["providers_list"][0].created_by, self.creator)
        self.assertEqual(len(resp.context["provider_relations"]), 1)
        self.assertEqual(len(resp.context["requirements_list"]), 0)
        self.assertEqual(resp.context["provider_relations"][0].data, user_data)
        self.assertEqual(
            resp.context["provider_relations"][0].provider, user_provider_rel.provider
        )
        self.assertIn(link_table_name, str(resp.content, "utf-8"))
