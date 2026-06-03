from django import template

register = template.Library()


@register.filter
def map_attr(value, arg):
    return [getattr(item, arg) for item in value]


@register.filter
def list(value):
    return list(value)
