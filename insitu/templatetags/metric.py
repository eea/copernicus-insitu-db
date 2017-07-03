from django import template


register = template.Library()


@register.simple_tag
def get_metric_value(form, field, attribute):
    return form.initial["_".join([field, attribute])]
