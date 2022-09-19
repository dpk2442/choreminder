from datetime import timedelta

from django import template

register = template.Library()


@register.filter(is_safe=True)
def format_duration(duration: timedelta):
    return "{:.0f}".format(duration.total_seconds())
