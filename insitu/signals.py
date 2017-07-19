import django.dispatch

data_resposible_updated = django.dispatch.Signal()


# delete index for soft deleted objects
product_deleted = django.dispatch.Signal()
requirement_deleted = django.dispatch.Signal()
data_deleted = django.dispatch.Signal()
data_responsible_deleted = django.dispatch.Signal()
