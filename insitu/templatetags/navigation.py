from django import template


register = template.Library()


@register.simple_tag(takes_context=True)
def active(context, url_name, return_value=" active"):
    return return_value if context.get("request").path == url_name else ""
