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

"""Module with the :class:`AccountSerializer` serializer class."""

from __future__ import annotations

from api.v1.serializers.mailbox_serializers import BaseMailboxSerializer

from .BaseAccountSerializer import BaseAccountSerializer


class AccountSerializer(BaseAccountSerializer):
    """The standard serializer for a :class:`core.models.Account`.

    Includes a nested serializer for the related field `mailboxes`.
    """

    mailboxes = BaseMailboxSerializer(many=True, read_only=True)
    """The mailboxes of the account are serialized
    by :class:`core.models.MailboxSerializers.BaseMailboxSerializer.BaseMailboxSerializer`.
    """
