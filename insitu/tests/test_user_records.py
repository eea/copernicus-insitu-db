from django.core.urlresolvers import reverse
from insitu import models
from insitu.tests import base


class UserRecordsTests(base.FormCheckTestCase):

    def test_list_provider_json(self):
        self.logging()
        user_data = base.DataFactory(created_by=self.creator)
        user_provider = base.DataProviderFactory(created_by=self.creator)
        user_provider_rel = base.DataProviderRelationFactory(
            created_by=self.creator,
            data=user_data,
            provider=user_provider,
        )
        resp = self.client.get(reverse('user_records', kwargs={"pk": self.creator.id}))
        self.assertEqual(resp.status_code, 200)
        import pdb; pdb.set_trace()
