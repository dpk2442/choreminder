from datetime import timedelta

from django import template

register = template.Library()


@register.filter(is_safe=True)
def format_duration(duration: timedelta):
    return "{:.0f}".format(duration.total_seconds())


@register.filter(is_safe=True)
def format_status_state(state: str):
    if state is None:
        return ""
    elif state == "completed":
        return "Completed"
    elif state == "due":
        return "Due"
    elif state == "overdue":
        return "Overdue"
