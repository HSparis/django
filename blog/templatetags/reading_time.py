"""Presentation helpers for plain-text articles; no database fields required."""
import math

from django import template
from django.utils.html import strip_tags

register = template.Library()


@register.filter
def reading_time(value):
    """Estimate minutes at 200 words per minute, rounding up to at least one."""
    words = len(strip_tags(str(value or "")).split())
    return max(1, math.ceil(words / 200))
