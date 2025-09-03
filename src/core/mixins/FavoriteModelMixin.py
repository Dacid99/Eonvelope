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

"""Module with the :class:`core.mixins.FavoriteMixin` mixin."""

from django.db.models import BooleanField, Model
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class FavoriteModelMixin(Model):
    """Mixin adding a `favorite` functionality to a model class."""

    is_favorite = BooleanField(
        default=False,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("favorite status"),
    )
    """Flags favorite accounts. False by default."""

    class Meta:
        """Metadata class for the mixin, abstract to avoid makemigrations picking it up."""

        abstract = True

    def toggle_favorite(self) -> None:
        """Toggles the `is_favorite` flag on the model instance."""
        self.is_favorite = not self.is_favorite
        self.save(update_fields=["is_favorite"])

    def get_absolute_toggle_favorite_url(self) -> str:
        """Gets the upload webview url for the model instance.

        Returns:
            The upload webview url for the model instance.
        """
        return reverse(
            f"api:v1:{self.BASENAME}-toggle-favorite", kwargs={"pk": self.pk}
        )
