import django.dispatch

data_provider_updated = django.dispatch.Signal()
requirement_updated = django.dispatch.Signal()


# delete index for soft deleted objects
product_deleted = django.dispatch.Signal()
requirement_deleted = django.dispatch.Signal()
data_deleted = django.dispatch.Signal()
data_provider_deleted = django.dispatch.Signal()
