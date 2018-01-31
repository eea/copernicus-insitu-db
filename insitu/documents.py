from django.conf import settings
from django.core.urlresolvers import reverse
from django_elasticsearch_dsl import DocType, Index, fields
from elasticsearch_dsl.analysis import analyzer, tokenizer, normalizer
from elasticsearch_dsl.search import Search

from insitu.models import Product, Requirement, DataProvider, Data
from insitu import signals

insitu = Index('insitu')
insitu.settings(max_result_window=settings.MAX_RESULT_WINDOW)

if not getattr(Search, '_patched', False):
    Search.order_by = Search.sort
    Search._patched = True

case_insensitive_analyzer = analyzer(
    'case_insensitive_analyzer',
    tokenizer=tokenizer('trigram', 'nGram'),
    filter=['lowercase']
)

case_insensitive_normalizer = normalizer(
    type="custom",
    name_or_instance='case_insensitive_normalizer',
    char_filter=[],
    filter="lowercase",
)


@insitu.doc_type
class ProductDoc(DocType):
    acronym = fields.KeywordField()
    name = fields.TextField(
        analyzer=case_insensitive_analyzer,
        fielddata=True,
        fields={'raw': fields.KeywordField(multi=True, ignore_above=256,
                                           normalizer=case_insensitive_normalizer)}
    )
    service = fields.KeywordField(attr='component.service.name')
    entity = fields.KeywordField(attr='component.entrusted_entity.acronym')
    component = fields.KeywordField(attr='component.name')
    group = fields.KeywordField(attr='group.name')
    status = fields.KeywordField(attr='status.name')
    area = fields.KeywordField(attr='area.name')

    def get_name_display(self):
        url = reverse('product:detail', kwargs={'pk': self.id})
        return '<a href="{url}">{name}</a>'.format(url=url, name=self.name)

    @staticmethod
    def delete_index(sender, **kwargs):
        document = ProductDoc.get(id=sender.id)
        document.delete()

    class Meta:
        model = Product
        fields = [
            'id',
            'description',
            'note',
        ]


@insitu.doc_type
class RequirementDoc(DocType):
    name = fields.TextField(
        analyzer=case_insensitive_analyzer,
        fielddata=True,
        fields={'raw': fields.KeywordField(multi=True, ignore_above=256,
                                           normalizer=case_insensitive_normalizer)}
    )
    dissemination = fields.KeywordField(attr='dissemination.name')
    quality_control_procedure = fields.KeywordField(
        attr='quality_control_procedure.name'
    )
    group = fields.KeywordField(attr='group.name')
    uncertainty = fields.KeywordField(attr='uncertainty.to_elastic_search_format')
    update_frequency = fields.KeywordField(
        attr='update_frequency.to_elastic_search_format')
    timeliness = fields.KeywordField(attr='timeliness.to_elastic_search_format')
    horizontal_resolution = fields.KeywordField(
        attr='horizontal_resolution.to_elastic_search_format')
    vertical_resolution = fields.KeywordField(
        attr='vertical_resolution.to_elastic_search_format')
    state = fields.KeywordField(attr='state.name')

    def get_name_display(self):
        url = reverse('requirement:detail', kwargs={'pk': self.id})
        return '<a href="{url}">{name}</a>'.format(url=url, name=self.name)

    @staticmethod
    def delete_index(sender, **kwargs):
        document = RequirementDoc.get(id=sender.id)
        document.delete()

    @staticmethod
    def update_index(sender, **kwargs):
        requirement = sender
        document = RequirementDoc.get(id=requirement.id)
        document.update(requirement)

    class Meta:
        model = Requirement
        fields = [
            'id',
            'note',
        ]


@insitu.doc_type
class DataDoc(DocType):
    name = fields.TextField(
        analyzer=case_insensitive_analyzer,
        fielddata=True,
        fields={'raw': fields.KeywordField(multi=True, ignore_above=256,
                                           normalizer=case_insensitive_normalizer)}
    )
    update_frequency = fields.KeywordField(attr='update_frequency.name')
    area = fields.KeywordField(attr='area.name')
    timeliness = fields.KeywordField(attr='timeliness.name')
    data_policy = fields.KeywordField(attr='data_policy.name')
    data_type = fields.KeywordField(attr='data_type.name')
    data_format = fields.KeywordField(attr='data_format.name')
    quality_control_procedure = fields.KeywordField(
        attr='quality_control_procedure.name'
    )
    dissemination = fields.KeywordField(attr='dissemination.name')
    state = fields.KeywordField(attr='state.name')

    def get_name_display(self):
        url = reverse('data:detail', kwargs={'pk': self.id})
        return '<a href="{url}">{name}</a>'.format(url=url, name=self.name)

    @staticmethod
    def delete_index(sender, **kwargs):
        document = DataDoc.get(id=sender.id)
        document.delete()

    class Meta:
        model = Data
        fields = [
            'id',
            'note'
        ]


@insitu.doc_type
class DataProviderDoc(DocType):
    name = fields.TextField(
        analyzer=case_insensitive_analyzer,
        fielddata=True,
        fields={
            'raw': fields.KeywordField(
                multi=True, ignore_above=256,
                normalizer=case_insensitive_normalizer
            )
        }
    )
    is_network = fields.BooleanField()
    acronym = fields.KeywordField(attr='get_elastic_search_data.acronym')
    address = fields.KeywordField(attr='get_elastic_search_data.address')
    phone = fields.KeywordField(attr='get_elastic_search_data.phone')
    email = fields.KeywordField(attr='get_elastic_search_data.email')
    contact_person = fields.KeywordField(
        attr='get_elastic_search_data.contact_person')
    provider_type = fields.KeywordField(
        attr='get_elastic_search_data.provider_type')
    state = fields.KeywordField(attr='state.name')

    class Meta:
        model = DataProvider
        fields = [
            'id',
            'description'
        ]

    def get_name_display(self):
        url = reverse('provider:detail', kwargs={'pk': self.id})
        return '<a href="{url}">{name}</a>'.format(url=url, name=self.name)

    def get_phone_display(self):
        return '<a href="tel:{phone}">{phone}</a>'.format(phone=self.phone)

    def get_email_display(self):
        return '<a href="mailto:{email}">{email}</a>'.format(email=self.email)

    @staticmethod
    def delete_index(sender, **kwargs):
        document = DataProviderDoc.get(id=sender.id)
        document.delete()

    @staticmethod
    def update_index(sender, **kwargs):
        data_provider = sender.data_provider
        document = DataProviderDoc.get(id=data_provider.id)
        document.update(data_provider)


signals.data_provider_updated.connect(DataProviderDoc.update_index)
signals.requirement_updated.connect(RequirementDoc.update_index)
signals.product_deleted.connect(ProductDoc.delete_index)
signals.requirement_deleted.connect(RequirementDoc.delete_index)
signals.data_deleted.connect(DataDoc.delete_index)
signals.data_provider_deleted.connect(DataProviderDoc.delete_index)
