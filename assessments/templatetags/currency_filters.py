from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='currency')
def currency(value):
    """
    Format a number as currency with commas and 2 decimal places.
    Example: 3500000 -> $3,500,000.00
    """
    if value is None:
        return "$0.00"

    try:
        # Convert to Decimal for precise decimal handling
        if isinstance(value, str):
            value = Decimal(value)
        elif not isinstance(value, Decimal):
            value = Decimal(str(value))

        # Format with commas and 2 decimal places
        return "${:,.2f}".format(float(value))
    except (ValueError, TypeError, InvalidOperation):
        return "$0.00"
