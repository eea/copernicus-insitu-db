from django.core.urlresolvers import reverse

from django_elasticsearch_dsl import DocType, Index, fields
from elasticsearch_dsl.search import Search

from insitu.models import DataGroup, Product, Requirement


insitu = Index('insitu')

if not getattr(Search, '_patched', False):
    Search.order_by = Search.sort
    Search._patched = True


@insitu.doc_type
class ProductDoc(DocType):
    acronym = fields.KeywordField()
    name = fields.KeywordField()
    group = fields.KeywordField(attr='group.name')
    status = fields.KeywordField(attr='status.name')
    service = fields.KeywordField(attr='component.service.name')
    entity = fields.KeywordField(attr='component.entrusted_entity.acronym')
    component = fields.KeywordField(attr='component.name')
    coverage = fields.KeywordField(attr='coverage.name')

    def get_name_display(self):
        url = reverse('product:detail', kwargs={'pk': self.id})
        return '<a href="{url}">{name}</a>'.format(url=url, name=self.name)

    class Meta:
        model = Product
        fields = [
            'id',
            'description',
            'note',
        ]


@insitu.doc_type
class RequirementDoc(DocType):
    name = fields.KeywordField()
    dissemination = fields.KeywordField(attr='dissemination.name')
    quality = fields.KeywordField(attr='quality.name')
    uncertainty = fields.KeywordField(attr='uncertainty.to_elastic_search_format')
    frequency = fields.KeywordField(attr='frequency.to_elastic_search_format')
    timeliness = fields.KeywordField(attr='timeliness.to_elastic_search_format')
    horizontal_resolution = fields.KeywordField(
        attr='horizontal_resolution.to_elastic_search_format')
    vertical_resolution = fields.KeywordField(
        attr='vertical_resolution.to_elastic_search_format')

    def get_name_display(self):
        url = reverse('requirement:detail', kwargs={'pk': self.id})
        return '<a href="{url}">{name}</a>'.format(url=url, name=self.name)

    class Meta:
        model = Requirement
        fields = [
            'id',
            'note',
        ]


@insitu.doc_type
class DataGroupDoc(DocType):
    name = fields.KeywordField()
    frequency = fields.KeywordField(attr='frequency.name')
    coverage = fields.KeywordField(attr='coverage.name')
    timeliness = fields.KeywordField(attr='timeliness.name')
    policy = fields.KeywordField(attr='policy.name')
    data_type = fields.KeywordField(attr='data_type.name')
    data_format = fields.KeywordField(attr='data_format.name')
    quality = fields.KeywordField(attr='quality.name')

    def get_name_display(self):
        url = reverse('data_group:detail', kwargs={'pk': self.id})
        return '<a href="{url}">{name}</a>'.format(url=url, name=self.name)

    class Meta:
        model = DataGroup
        fields = [
            'id',
            'note'
        ]
