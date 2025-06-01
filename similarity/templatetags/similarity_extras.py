from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value
    
@register.filter
def percentage(value):
    """Converts a decimal to a percentage"""
    try:
        return int(float(value) * 100)
    except (ValueError, TypeError):
        return value
