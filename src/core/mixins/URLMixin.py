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

"""Module with the :class:`core.mixins.URLMixin` mixin."""

from django.urls import reverse


class URLMixin:
    """Mixin to add url features to a :class:`django.db.models.Model`."""

    BASENAME = ""

    def get_absolute_url(self) -> str:
        """Gets the detail webview url for the model instance.

        Note:
            Used by :class:`django.views.generics.ModelFormMixin` for redirection.

        Returns:
            The detail webview url for the model instance.
        """
        return reverse("web:" + self.get_detail_web_url_name(), kwargs={"pk": self.pk})

    def get_absolute_edit_url(self) -> str:
        """Gets the edit webview url for the model instance.

        Returns:
            The edit webview url for the model instance.
        """
        return reverse("web:" + self.get_edit_web_url_name(), kwargs={"pk": self.pk})

    def get_absolute_list_url(self) -> str:
        """Gets the list webview url for the model instance.

        Returns:
            The list webview url for the model instance.
        """
        return reverse("web:" + self.get_list_web_url_name())

    def get_absolute_table_url(self) -> str:
        """Gets the table webview url for the model instance.

        Returns:
            The table webview url for the model instance.
        """
        return reverse("web:" + self.get_table_web_url_name())

    def get_absolute_api_list_url(self) -> str:
        """Gets the list api url for the model instance.

        Returns:
            The list api url for the model instance.
        """
        return reverse("api:v1:" + self.BASENAME + "-list")

    @classmethod
    def get_list_web_url_name(cls) -> str:
        """Gets the list webview urlname for the model.

        Returns:
            The list webview urlname for the model.
        """
        return cls.BASENAME + "-filter-list"

    @classmethod
    def get_table_web_url_name(cls) -> str:
        """Gets the list webview urlname for the model.

        Returns:
            The list webview urlname for the model.
        """
        return cls.BASENAME + "-table"

    @classmethod
    def get_detail_web_url_name(cls) -> str:
        """Gets the detail webview urlname for the model.

        Returns:
            The detail webview urlname for the model.
        """
        return cls.BASENAME + "-detail"

    @classmethod
    def get_edit_web_url_name(cls) -> str:
        """Gets the edit webview urlname for the model.

        Returns:
            The edit webview urlname for the model.
        """
        return cls.BASENAME + "-edit"
