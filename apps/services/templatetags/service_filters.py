from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

@register.filter(name='format_currency')
def format_currency(value):
    try:
        # Chuyển đổi thành integer và format với dấu chấm
        return intcomma(int(float(value)))
    except (ValueError, TypeError):
        return value

@register.filter
def intdot(value):
    try:
        value = int(float(value))
        return '{:,}'.format(value).replace(',', '.')
    except (ValueError, TypeError):
        return value 