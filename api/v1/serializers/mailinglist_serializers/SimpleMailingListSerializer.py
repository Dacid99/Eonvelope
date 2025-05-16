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

"""Module with the :class:`SimpleMailingListSerializer` serializer class."""

# ruff: noqa: TC001 TC002
# TYPE_CHECKING guard doesnt work with drf-spectacular: https://github.com/tfranzel/drf-spectacular/issues/390

from __future__ import annotations

from typing import Any

from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict

from core.models.MailingList import MailingList

from ..email_serializers.BaseEmailSerializer import BaseEmailSerializer
from .BaseMailingListSerializer import BaseMailingListSerializer


class SimpleMailingListSerializer(BaseMailingListSerializer):
    """A reduced serializer for a :class:`core.models.MailingList.MailingList`.

    Includes a method field for the count of elements in :attr:`core.models.MailingList.MailingList.emails`.
    """

    emails = serializers.SerializerMethodField(read_only=True)
    """The mails by the mailinglist. Set via :func:`get_emails`."""

    def get_emails(self, instance: MailingList) -> ReturnDict[str, Any]:
        """Serializes the correspondents connected to the instance to be serialized.

        Args:
            instance: The instance being serialized.

        Returns:
            The serialized From correspondents connected to the instance to be serialized.
        """
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user is not None:
            emails = instance.emails.filter(mailbox__account__user=user)
        else:
            emails = instance.emails.none()
        return BaseEmailSerializer(emails, many=True, read_only=True).data
