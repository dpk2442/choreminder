from datetime import timedelta
from typing import List

from django import template

from chores import model_views

register = template.Library()


@register.filter(is_safe=True)
def format_duration(duration: timedelta):
    return "{:.0f}".format(duration.total_seconds())


@register.filter(is_safe=True)
def format_tag_list(tags: List[model_views.Tag]):
    return ", ".join(map(lambda tag: tag.name, tags))
