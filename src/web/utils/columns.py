from typing import override

from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django_tables2 import Column


class CheckboxColumn(Column):
    @override
    def __init__(self, *args, **kwargs):
        kwargs.update(
            {
                "verbose_name": "",
                "empty_values": (),
                "orderable": False,
                "exclude_from_export": True,
            }
        )
        super().__init__(*args, **kwargs)

    @override
    def render(self, record):
        return format_html(
            """<label for="select-{id}" class="form-check-label visually-hidden">{select_string}</label>
            <input class="form-check-input ms-2" type="checkbox" id="select-{id}" data-id="{id}"/>
            """,
            id=record.id,
            select_string=_("Select"),
        )


class IsFavoriteColumn(Column):
    @override
    def render(self, record):
        return format_html(
            """<span class="btn badge {favorite_badge_bg} shadow mx-1 favorite-badge"
                    data-url="{toggle_favorite_url}"
                    {aria_label}>
                    <i class="fa-regular fa-star" aria-hidden="true"></i>
                </span>
            """,
            toggle_favorite_url=record.get_absolute_toggle_favorite_url(),
            favorite_badge_bg="bg-warning" if record.is_favorite else "bg-secondary",
            aria_label='aria-label="{favorite_string}"'.format(
                favorite_string=_("Favorite")
            ),
        )


class IsHealthyColumn(Column):
    @override
    def __init__(self, *args, **kwargs):
        kwargs.update({"empty_values": ()})
        super().__init__(*args, **kwargs)

    @override
    def render(self, value):
        if value:
            string_template = """<span class="badge bg-success text-end shadow"
            aria-label="{health_string}">
            <i class="fa-regular fa-circle-check" aria-hidden="true"></i>
            </span>"""
            health_string = _("Healthy")
        elif value is False:
            string_template = """<span class="badge bg-danger text-end shadow"
                aria-label="{health_string}">
                <i class="fa-solid fa-triangle-exclamation" aria-hidden="true"></i>
            </span>"""
            health_string = _("Unhealthy")
        else:
            string_template = """<span class="badge bg-secondary text-end shadow"
                aria-label="{health_string}">
                <i class="fa-regular fa-circle-question" aria-hidden="true"></i>
            </span>"""
            health_string = _("Health unknown")

        return format_html(string_template, health_string=health_string)
