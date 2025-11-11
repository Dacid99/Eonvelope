# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Eonvelope - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Eonvelope Contributors
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

"""Module with the :class:`core.mixins.UploadMixin` mixin."""

from typing import Any, ClassVar, Protocol

from django.urls import reverse


class Uploadable(Protocol):
    """Protocol defining the required attributes of a class implementing this mixin."""

    BASENAME: ClassVar[str]
    pk: Any


class UploadMixin:
    """Mixin providing url methods for the upload page of the model."""

    @classmethod
    def get_upload_web_url_name(cls: type[Uploadable]) -> str:
        """Gets the edit webview urlname for the model.

        Returns:
            The edit webview urlname for the model.
        """
        return cls.BASENAME + "-upload"

    def get_absolute_upload_url(self: Uploadable) -> str:
        """Gets the upload webview url for the model instance.

        Returns:
            The upload webview url for the model instance.
        """
        return reverse("web:" + self.get_upload_web_url_name(), kwargs={"pk": self.pk})
