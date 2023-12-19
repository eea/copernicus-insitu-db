from django import template


register = template.Library()


@register.simple_tag
def get_metric_value(form, field, attribute):
    if form.data:
        return form.data["__".join([field, attribute])]
    elif form.initial:
        return form.initial["__".join([field, attribute])]


@register.filter(name="get_field_nice_value")
def get_model_attribute(object, attribute):
    field = object._meta.get_field(attribute)
    if field.choices:
        for value, choice in field.flatchoices:
            if value == getattr(object, attribute):
                return choice
    return getattr(object, attribute)


@register.filter(name="has_group")
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter(name="check_group")
def check_group(groups, group_name):
    return group_name in groups


@register.simple_tag
def has_user_perm(obj, user):
    return obj.has_user_perm(user)
