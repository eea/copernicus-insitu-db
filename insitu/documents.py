from django.core.urlresolvers import reverse
from django_elasticsearch_dsl import DocType, Index, fields
from elasticsearch_dsl.search import Search

from insitu.models import Product, Requirement, DataResponsible, Data
from insitu import signals

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
    name = fields.KeywordField()
    dissemination = fields.KeywordField(attr='dissemination.name')
    quality_control_procedure = fields.KeywordField(
        attr='quality_control_procedure.name'
    )
    group = fields.KeywordField(attr='group.name')
    uncertainty = fields.KeywordField(attr='uncertainty.to_elastic_search_format')
    update_frequency = fields.KeywordField(attr='update_frequency.to_elastic_search_format')
    timeliness = fields.KeywordField(attr='timeliness.to_elastic_search_format')
    horizontal_resolution = fields.KeywordField(
        attr='horizontal_resolution.to_elastic_search_format')
    vertical_resolution = fields.KeywordField(
        attr='vertical_resolution.to_elastic_search_format')

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
    name = fields.KeywordField()
    update_frequency = fields.KeywordField(attr='update_frequency.name')
    coverage = fields.KeywordField(attr='coverage.name')
    timeliness = fields.KeywordField(attr='timeliness.name')
    policy = fields.KeywordField(attr='policy.name')
    data_type = fields.KeywordField(attr='data_type.name')
    data_format = fields.KeywordField(attr='data_format.name')
    quality_control_procedure = fields.KeywordField(
        attr='quality_control_procedure.name'
    )
    dissemination = fields.KeywordField(attr='dissemination.name')


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
class DataResponsibleDoc(DocType):
    name = fields.KeywordField()
    is_network = fields.BooleanField()
    acronym = fields.KeywordField(attr='get_elastic_search_data.acronym')
    address = fields.KeywordField(attr='get_elastic_search_data.address')
    phone = fields.KeywordField(attr='get_elastic_search_data.phone')
    email = fields.KeywordField(attr='get_elastic_search_data.email')
    contact_person = fields.KeywordField(
        attr='get_elastic_search_data.contact_person')
    responsible_type = fields.KeywordField(
        attr='get_elastic_search_data.responsible_type')

    class Meta:
        model = DataResponsible
        fields = [
            'id',
            'description'
        ]

    def get_name_display(self):
        url = reverse('responsible:detail', kwargs={'pk': self.id})
        return '<a href="{url}">{name}</a>'.format(url=url, name=self.name)

    @staticmethod
    def delete_index(sender, **kwargs):
        document = DataResponsibleDoc.get(id=sender.id)
        document.delete()

    @staticmethod
    def update_index(sender, **kwargs):
        data_responsible = sender.data_responsible
        document = DataResponsibleDoc.get(id=data_responsible.id)
        document.update(data_responsible)

signals.data_resposible_updated.connect(DataResponsibleDoc.update_index)
signals.requirement_updated.connect(RequirementDoc.update_index)
signals.product_deleted.connect(ProductDoc.delete_index)
signals.requirement_deleted.connect(RequirementDoc.delete_index)
signals.data_deleted.connect(DataDoc.delete_index)
signals.data_responsible_deleted.connect(DataResponsibleDoc.delete_index)
