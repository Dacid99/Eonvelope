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

"""Module with the :class:`api.v1.mixins.ToggleFavoriteMixin` viewset mixin."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import action
from rest_framework.response import Response


if TYPE_CHECKING:
    from rest_framework.request import Request


class ToggleFavoriteMixin:
    """Mixin providing a toggle-favorite action for a viewset."""

    URL_PATH_TOGGLE_FAVORITE = "toggle-favorite"
    URL_NAME_TOGGLE_FAVORITE = "toggle-favorite"

    @action(
        detail=True,
        methods=["post"],
        url_path=URL_PATH_TOGGLE_FAVORITE,
        url_name=URL_NAME_TOGGLE_FAVORITE,
    )
    def toggle_favorite(self, request: Request, pk: int | None = None) -> Response:
        """Action method toggling the favorite flag of the object.

        Args:
            request: The request triggering the action.
            pk: The private key of the object to toggle favorite. Defaults to None.

        Returns:
            A response detailing the request status.
        """
        toggle_object = self.get_object()
        toggle_object.is_favorite = not toggle_object.is_favorite
        toggle_object.save(update_fields=["is_favorite"])
        if toggle_object.is_favorite:
            message = _("%(object)s marked as favorite.") % {"object": toggle_object}
        else:
            message = _("%(object)s unmarked as favorite.") % {"object": toggle_object}
        return Response({"detail": message})
