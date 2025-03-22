from django import template

register = template.Library()

@register.filter
def floatformat(value, arg=1):
    """
    Formats a float to a specified number of decimal places.
    """
    try:
        value = float(value)
        arg = int(arg)
        return round(value, arg)
    except (ValueError, TypeError):
        return value

@register.filter
def stringformat(value, arg):
    """
    Formats a value according to the arg, a string formatting specifier.
    """
    try:
        return format(value, arg)
    except (ValueError, TypeError):
        return value

@register.filter
def slice(value, arg):
    """
    Returns a slice of the value.
    """
    try:
        bits = []
        for x in arg.split(':'):
            if not x:
                bits.append(None)
            else:
                bits.append(int(x))
        return value[slice(*bits)]
    except (ValueError, TypeError):
        return value

from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplie la valeur par l'argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

