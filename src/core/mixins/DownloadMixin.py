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

"""Module with the :class:`core.mixins.DownloadMixin` mixin."""

from django.urls import reverse


class DownloadMixin:
    """Mixin providing a property to check whether a model instance provides a download.

    Designed for use in combination with :class:`core.mixins.FilePathModelMixin`.
    """

    @property
    def has_download(self) -> bool:
        """Checks whether a download is possible for the instance."""
        return bool(self.file_path)

    def get_absolute_download_url(self) -> str:
        """Returns the url of the download api endpoint."""
        return reverse(f"api:v1:{self.BASENAME}-download", kwargs={"pk": self.pk})
