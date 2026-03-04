from django import template

register = template.Library()

@register.filter
def split(value, sep=','):
    """Split a string by sep (default: ',') and return a list."""
    if not value:
        return []
    return [v.strip() for v in value.split(sep)]
