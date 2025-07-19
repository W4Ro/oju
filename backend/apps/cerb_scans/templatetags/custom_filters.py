from django import template

register = template.Library()

@register.filter
def get(dictionary, key):
    """return the value of a dictionary key"""
    return dictionary.get(key)
