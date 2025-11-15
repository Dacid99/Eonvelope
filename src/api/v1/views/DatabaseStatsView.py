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

"""Module with the :class:`DatabaseStatsView` apiview."""

from __future__ import annotations

from typing import TYPE_CHECKING

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.v1.serializers import DatabaseStatsSerializer


if TYPE_CHECKING:
    from rest_framework.request import Request


@extend_schema_view(
    get=extend_schema(
        description="Gets all the number of entries in the tables of the database."
    )
)
class DatabaseStatsView(APIView):
    """APIView for the statistics of the database."""

    NAME = "stats"
    permission_classes = [IsAuthenticated]
    serializer_class = DatabaseStatsSerializer

    def get(self, request: Request) -> Response:
        """Gets all the number of entries in the tables of the database.

        Args:
            request: The GET request to respond to.

        Returns:
            A dictionary with the count of the table entries.
        """
        data = self.serializer_class({}, context={"request": request}).data
        return Response(data)
