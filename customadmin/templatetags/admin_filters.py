from django import template

register = template.Library()



@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0  # Return 0 i

# Custom filter to divide values
@register.filter
def div(value, arg):
    try:
        return value / float(arg)
    except (ValueError, TypeError):
        return 0

# Custom filter to get item from a dictionary
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
