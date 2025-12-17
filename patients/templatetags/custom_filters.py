from django import template

register = template.Library()


@register.filter
def ordinal(value):
    try:
        value = int(value)
        if 10 <= value % 100 <= 20:
            suffix = "th"
        elif value == 0:
            suffix = " "
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(value % 10, "th")
        return f"{value}{suffix}"
    except (TypeError, ValueError):
        return value

@register.filter
def humanize_snake_case(value):
    return " ".join(word.capitalize() for word in value.split("_"))
