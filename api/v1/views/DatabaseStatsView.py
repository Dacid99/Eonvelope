# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer
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

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Account, Attachment, Correspondent, Email, Mailbox


if TYPE_CHECKING:
    from rest_framework.request import Request


class DatabaseStatsView(APIView):
    """APIView for the statistics of the database."""

    NAME = "stats"
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """Gets all the number of entries in the tables of the database.

        Args:
            request: The GET request to respond to.

        Returns:
            A dictionary with the count of the table entries.
        """
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_404_NOT_FOUND)

        email_count = Email.objects.filter(mailbox__account__user=request.user).count()
        correspondent_count = (
            Correspondent.objects.filter(emails__mailbox__account__user=request.user)
            .distinct()
            .count()
        )
        attachment_count = Attachment.objects.filter(
            email__mailbox__account__user=request.user
        ).count()
        account_count = Account.objects.filter(user=request.user).count()
        mailbox_count = Mailbox.objects.filter(account__user=request.user).count()

        return Response(
            {
                "email_count": email_count,
                "correspondent_count": correspondent_count,
                "attachment_count": attachment_count,
                "account_count": account_count,
                "mailbox_count": mailbox_count,
            }
        )
