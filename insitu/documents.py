from django_elasticsearch_dsl import DocType, Index, fields
from elasticsearch_dsl.search import Search

from insitu.models import Product


insitu = Index('insitu')

if not getattr(Search, '_patched', False):
    Search.order_by = Search.sort
    Search._patched = True


@insitu.doc_type
class ProductDoc(DocType):
    acronym = fields.KeywordField()
    name = fields.KeywordField()
    group = fields.KeywordField(attr='group.name')
    service = fields.KeywordField(attr='component.service.name')
    entity = fields.KeywordField(attr='component.entrusted_entity.acronym')
    component = fields.KeywordField(attr='component.name')
    coverage = fields.KeywordField(attr='coverage.name')

    class Meta:
        model = Product
        fields = [
            'description',
            'note',
        ]
