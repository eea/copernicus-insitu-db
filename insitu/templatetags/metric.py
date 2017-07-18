from django import template


register = template.Library()


@register.simple_tag
def get_metric_value(form, field, attribute):
    if form.data:
        return form.data["_".join([field, attribute])]
    elif form.initial:
        return form.initial["_".join([field, attribute])]
