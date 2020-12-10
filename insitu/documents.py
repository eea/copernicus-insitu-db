from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import Prefetch
from django_elasticsearch_dsl import DocType, Index, fields
from elasticsearch_dsl.analysis import analyzer, tokenizer, normalizer
from elasticsearch_dsl.search import Search

from insitu.models import (
    Data,
    DataRequirement,
    DataProvider,
    Product,
    ProductRequirement,
    Requirement,
    Component,
)
from insitu import signals

insitu_products = Index("insitu_products")
insitu_requirements = Index("insitu_requirements")
insitu_data = Index("insitu_data")
insitu_dataproviders = Index("insitu_dataproviders")

ELASTICSEARCH_INDEX_SETTINGS = {
    "max_result_window": settings.MAX_RESULT_WINDOW,
    "number_of_shards": 1,
    "number_of_replicas": 0,
}

insitu_products.settings(**ELASTICSEARCH_INDEX_SETTINGS)
insitu_requirements.settings(**ELASTICSEARCH_INDEX_SETTINGS)
insitu_data.settings(**ELASTICSEARCH_INDEX_SETTINGS)
insitu_dataproviders.settings(**ELASTICSEARCH_INDEX_SETTINGS)

if not getattr(Search, "_patched", False):
    Search.order_by = Search.sort
    Search._patched = True

case_insensitive_analyzer = analyzer(
    "case_insensitive_analyzer",
    tokenizer=tokenizer("trigram", "nGram"),
    filter=["lowercase"],
)

case_insensitive_normalizer = normalizer(
    type="custom",
    name_or_instance="case_insensitive_normalizer",
    char_filter=[],
    filter="lowercase",
)


@insitu_products.doc_type
class ProductDoc(DocType):
    acronym = fields.KeywordField()
    description = fields.TextField()
    name = fields.TextField(
        analyzer=case_insensitive_analyzer,
        fielddata=True,
        fields={
            "raw": fields.KeywordField(
                multi=True, ignore_above=256, normalizer=case_insensitive_normalizer
            )
        },
    )
    group = fields.KeywordField(attr="group.name")
    status = fields.KeywordField(attr="status.name")
    service = fields.KeywordField(attr="component.service.name")
    entity = fields.KeywordField(attr="component.entrusted_entity.acronym")
    component = fields.KeywordField(attr="component.name")
    area = fields.KeywordField(attr="area.name")
    note = fields.TextField()

    def get_name_display(self):
        url = reverse("product:detail", kwargs={"pk": self.id})
        return '<a href="{url}">{name}</a>'.format(url=url, name=self.name)

    @staticmethod
    def delete_index(sender, **kwargs):
        document = ProductDoc.get(id=sender.id)
        document.delete()

    class Meta:
        model = Product
        fields = [
            "id",
        ]


@insitu_requirements.doc_type
class RequirementDoc(DocType):
    name = fields.TextField(
        analyzer=case_insensitive_analyzer,
        fielddata=True,
        fields={
            "raw": fields.KeywordField(
                multi=True, ignore_above=256, normalizer=case_insensitive_normalizer
            )
        },
    )
    dissemination = fields.KeywordField(attr="dissemination.name")
    quality_control_procedure = fields.KeywordField(
        attr="quality_control_procedure.name"
    )
    group = fields.KeywordField(attr="group.name")
    uncertainty = fields.KeywordField(attr="uncertainty.to_elastic_search_format")
    update_frequency = fields.KeywordField(
        attr="update_frequency.to_elastic_search_format"
    )
    timeliness = fields.KeywordField(attr="timeliness.to_elastic_search_format")
    scale = fields.KeywordField(attr="scale.to_elastic_search_format")
    horizontal_resolution = fields.KeywordField(
        attr="horizontal_resolution.to_elastic_search_format"
    )
    vertical_resolution = fields.KeywordField(
        attr="vertical_resolution.to_elastic_search_format"
    )
    state = fields.KeywordField(attr="state.name")

    products = fields.ObjectField(
        attr="product_requirements",
        properties={
            "product": fields.KeywordField(attr="product.name"),
        },
    )
    components = fields.ObjectField(
        attr="product_requirements",
        properties={
            "component": fields.KeywordField(attr="product.component.name"),
        },
    )

    note = fields.TextField()

    def get_name_display(self):
        url = reverse("requirement:detail", kwargs={"pk": self.id})
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
        related_models = [ProductRequirement, Product]
        fields = [
            "id",
        ]

    def get_queryset(self):
        """
        Not mandatory but to improve performance we can select related in one sql
        request.
        """
        return (
            super(RequirementDoc, self)
            .get_queryset()
            .prefetch_related("product_requirements__product")
        )

    def get_instances_from_related(self, related_instance):
        """
        If related_models is set, define how to retrieve the Requirement
        instance(s) from the related model. The related_models option should be
        used with caution because it can lead in the index to the updating of a
        lot of items.
        """
        if isinstance(related_instance, ProductRequirement):
            return related_instance.requirement
        if isinstance(related_instance, Product):
            return related_instance.requirements.all()


@insitu_data.doc_type
class DataDoc(DocType):
    name = fields.TextField(
        analyzer=case_insensitive_analyzer,
        fielddata=True,
        fields={
            "raw": fields.KeywordField(
                multi=True, ignore_above=256, normalizer=case_insensitive_normalizer
            )
        },
    )
    update_frequency = fields.KeywordField(attr="update_frequency.name")
    area = fields.KeywordField(attr="area.name")
    timeliness = fields.KeywordField(attr="timeliness.name")
    data_policy = fields.KeywordField(attr="data_policy.name")
    data_type = fields.KeywordField(attr="data_type.name")
    data_format = fields.KeywordField(attr="data_format.name")
    quality_control_procedure = fields.KeywordField(
        attr="quality_control_procedure.name"
    )
    dissemination = fields.KeywordField(attr="dissemination.name")
    requirements = fields.ObjectField(
        attr="requirements_get_filtered",
        properties={
            "requirement": fields.KeywordField(attr="name"),
        },
    )
    state = fields.KeywordField(attr="state.name")
    note = fields.TextField()

    def get_name_display(self):
        url = reverse("data:detail", kwargs={"pk": self.id})
        return '<a href="{url}">{name}</a>'.format(url=url, name=self.name)

    @staticmethod
    def delete_index(sender, **kwargs):
        document = DataDoc.get(id=sender.id)
        document.delete()

    class Meta:
        model = Data
        related_models = [DataRequirement, Requirement]
        fields = [
            "id",
        ]

    def get_queryset(self):
        """
        Not mandatory but to improve performance we can select related in one sql
        request.
        """
        prefetch = Prefetch(
            "datarequirement_set__requirement",
            queryset=DataRequirement.objects.filter(
                _deleted=False, requirement___deleted=False
            ),
        )
        return super(DataDoc, self).get_queryset().prefetch_related(prefetch)

    def get_instances_from_related(self, related_instance):
        """
        If related_models is set, define how to retrieve the Data instance(s)
        from the related model. The related_models option should be used with
        caution because it can lead in the index to the updating of a lot of items.
        """
        if isinstance(related_instance, DataRequirement):
            return related_instance.data
        if isinstance(related_instance, Requirement):
            return [
                datarequirement.data
                for datarequirement in related_instance.datarequirement_set.all()
            ]


@insitu_dataproviders.doc_type
class DataProviderDoc(DocType):
    name = fields.TextField(
        analyzer=case_insensitive_analyzer,
        fielddata=True,
        fields={
            "raw": fields.KeywordField(
                multi=True, ignore_above=256, normalizer=case_insensitive_normalizer
            )
        },
    )
    description = fields.TextField()
    is_network = fields.BooleanField()
    acronym = fields.KeywordField(attr="get_elastic_search_data.acronym")
    address = fields.KeywordField(attr="get_elastic_search_data.address")
    phone = fields.KeywordField(attr="get_elastic_search_data.phone")
    email = fields.KeywordField(attr="get_elastic_search_data.email")
    contact_person = fields.KeywordField(attr="get_elastic_search_data.contact_person")
    provider_type = fields.KeywordField(attr="get_elastic_search_data.provider_type")
    state = fields.KeywordField(attr="state.name")

    components = fields.ObjectField(
        attr="components",
        properties={
            "name": fields.KeywordField(attr="name"),
        },
    )

    class Meta:
        model = DataProvider
        fields = ["id"]
        related_models = [ProductRequirement, Component]

    def get_name_display(self):
        url = reverse("provider:detail", kwargs={"pk": self.id})
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

    def get_instances_from_related(self, related_instance):
        """
        If related_models is set, define how to retrieve the Requirement
        instance(s) from the related model. The related_models option should be
        used with caution because it can lead in the index to the updating of a
        lot of items.
        """
        if isinstance(related_instance, ProductRequirement):
            return DataProvider.objects.filter(
                data__requirements__product_requirements=related_instance
            )
        if isinstance(related_instance, Component):
            return DataProvider.objects.filter(
                data__requirements__products__component=related_instance
            )


signals.data_provider_updated.connect(DataProviderDoc.update_index)
signals.requirement_updated.connect(RequirementDoc.update_index)
signals.product_deleted.connect(ProductDoc.delete_index)
signals.requirement_deleted.connect(RequirementDoc.delete_index)
signals.data_deleted.connect(DataDoc.delete_index)
signals.data_provider_deleted.connect(DataProviderDoc.delete_index)
