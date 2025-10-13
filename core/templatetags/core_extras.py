from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """Template filter to look up dictionary values by key."""
    if dictionary and hasattr(dictionary, 'get'):
        return dictionary.get(key)
    return None

@register.filter
def transaction_count_display(count):
    """Display transaction count with 100+ for counts over 100."""
    if count is None:
        return "0"
    if count > 100:
        return "100+"
    return str(count)