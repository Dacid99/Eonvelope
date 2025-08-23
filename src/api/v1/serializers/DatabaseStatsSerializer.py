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

"""Module with the :class:`DatabaseStatsSerializer` serializer."""

from typing import Any

from rest_framework import serializers

from core.models import Account, Attachment, Correspondent, Email, Mailbox


class DatabaseStatsSerializer(serializers.Serializer):
    """Serializer for the stats of the database."""

    email_count = serializers.SerializerMethodField(read_only=True)
    correspondent_count = serializers.SerializerMethodField(read_only=True)
    attachment_count = serializers.SerializerMethodField(read_only=True)
    account_count = serializers.SerializerMethodField(read_only=True)
    mailbox_count = serializers.SerializerMethodField(read_only=True)

    def get_email_count(self, obj: Any) -> int:
        """Gets the count of emails for the user.

        Returns:
            The number of emails belonging to the user.
        """
        request = self.context.get("request")
        user = getattr(request, "user", None)
        return Email.objects.filter(mailbox__account__user=user).count()

    def get_correspondent_count(self, obj: Any) -> int:
        """Gets the count of correspondents for the user.

        Returns:
            The number of correspondents belonging to the user.
        """
        request = self.context.get("request")
        user = getattr(request, "user", None)
        return Correspondent.objects.filter(user=user).distinct().count()

    def get_attachment_count(self, obj: Any) -> int:
        """Gets the count of attachments for the user.

        Returns:
            The number of attachments belonging to the user.
        """
        request = self.context.get("request")
        user = getattr(request, "user", None)
        return Attachment.objects.filter(email__mailbox__account__user=user).count()

    def get_account_count(self, obj: Any) -> int:
        """Gets the count of accounts for the user.

        Returns:
            The number of accounts belonging to the user.
        """
        request = self.context.get("request")
        user = getattr(request, "user", None)
        return Account.objects.filter(user=user).count()

    def get_mailbox_count(self, obj: Any) -> int:
        """Gets the count of mailboxes for the user.

        Returns:
            The number of mailboxes belonging to the user.
        """
        request = self.context.get("request")
        user = getattr(request, "user", None)
        return Mailbox.objects.filter(account__user=user).count()
