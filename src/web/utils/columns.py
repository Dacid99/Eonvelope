# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Emailkasten Contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""Module with custom columns classes."""

from typing import Any, override

from django.db.models import Model
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django_tables2 import Column


class CheckboxColumn(Column):
    """Column with select checkboxes matching the templates."""

    @override
    def __init__(self, *args: list[Any], **kwargs: dict[str, Any]) -> None:
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
    def render(self, record: Model) -> str:  # pylint: disable=arguments-renamed
        """Renders the select checkbox for the record.

        Args:
            record: The model record.

        Returns:
            Html checkbox for selecting the instance.
        """
        return format_html(
            """<label for="select-{id}" class="form-check-label visually-hidden">{select_string}</label>
            <input class="form-check-input ms-2" type="checkbox" id="select-{id}" data-id="{id}"/>
            """,
            id=record.id,
            select_string=_("Select"),
        )


class IsFavoriteColumn(Column):
    """Column for the is_favorite field with the badge."""

    @override
    def render(self, record: Model) -> str:  # pylint: disable=arguments-renamed
        """Renders the value in form of a badge.

        Args:
            record: The model with the is_favorite field.

        Returns:
            Html badge for the favorite status.
        """
        return format_html(
            """<span class="btn badge {favorite_badge_bg} shadow mx-1 favorite-badge"
                    data-url="{toggle_favorite_url}"
                    {aria_label}>
                    <i class="fa-regular fa-star" aria-hidden="true"></i>
                </span>
            """,
            toggle_favorite_url=record.get_absolute_toggle_favorite_url(),
            favorite_badge_bg="bg-warning" if record.is_favorite else "bg-secondary",
            aria_label=f'aria-label="{_("Favorite")}"',
        )


class IsHealthyColumn(Column):
    """Column for the is_healthy field with the badge."""

    @override
    def __init__(self, *args: list[Any], **kwargs: dict[str, Any]) -> None:
        kwargs.update({"empty_values": ()})
        super().__init__(*args, **kwargs)

    @override
    def render(self, value: bool) -> str:
        """Renders the value in form of a badge.

        Args:
            value: The value of the is_healthy field.

        Returns:
            Html badge for the health status.
        """
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
