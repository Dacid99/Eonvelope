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

from typing import TYPE_CHECKING, Final

from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from core.models.AccountModel import AccountModel
from core.models.AttachmentModel import AttachmentModel
from core.models.CorrespondentModel import CorrespondentModel
from core.models.EMailModel import EMailModel
from core.models.MailboxModel import MailboxModel
from core.models.MailingListModel import MailingListModel

from ..serializers.DatabaseStatsSerializer import DatabaseStatsSerializer


if TYPE_CHECKING:
    from rest_framework.permissions import BasePermission


class DatabaseStatsView(RetrieveAPIView):
    """APIView for the statistics of the database."""

    NAME = "stats"
    permission_classes: Final[list[type[BasePermission]]] = [IsAuthenticated]
    serializer_class = DatabaseStatsSerializer

    def get_object(self) -> dict:
        """Gets all the number of entries in the tables of the database.

        Returns:
            A dictionary with the count of the table entries.
        """
        email_count = EMailModel.objects.filter(
            mailbox__account__user=self.request.user
        ).count()
        correspondent_count = (
            CorrespondentModel.objects.filter(
                emails__mailbox__account__user=self.request.user
            )
            .distinct()
            .count()
        )
        attachment_count = AttachmentModel.objects.filter(
            email__mailbox__account__user=self.request.user
        ).count()
        account_count = AccountModel.objects.filter(user=self.request.user).count()
        mailbox_count = MailboxModel.objects.filter(
            account__user=self.request.user
        ).count()
        mailinglist_count = (
            MailingListModel.objects.filter(
                emails__mailbox__account__user=self.request.user
            )
            .distinct()
            .count()
        )
        return {
            "email_count": email_count,
            "correspondent_count": correspondent_count,
            "attachment_count": attachment_count,
            "account_count": account_count,
            "mailbox_count": mailbox_count,
            "mailinglist_count": mailinglist_count,
        }
