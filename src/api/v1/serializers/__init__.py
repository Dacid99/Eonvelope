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

"""api.v1.serializers package containing serializers for the Emailkasten API version 1."""

from .account_serializers import AccountSerializer, BaseAccountSerializer
from .attachment_serializers import BaseAttachmentSerializer
from .correspondent_serializers import (
    BaseCorrespondentSerializer,
    CorrespondentSerializer,
)
from .daemon_serializers import BaseDaemonSerializer
from .DatabaseStatsSerializer import DatabaseStatsSerializer
from .email_serializers import BaseEmailSerializer, EmailSerializer, FullEmailSerializer
from .emailcorrespondent_serializers import (
    BaseEmailCorrespondentSerializer,
    CorrespondentEmailSerializer,
    EmailCorrespondentSerializer,
)
from .mailbox_serializers import BaseMailboxSerializer, MailboxWithDaemonSerializer


__all__ = [
    "AccountSerializer",
    "BaseAccountSerializer",
    "BaseAttachmentSerializer",
    "BaseCorrespondentSerializer",
    "BaseDaemonSerializer",
    "BaseEmailCorrespondentSerializer",
    "BaseEmailSerializer",
    "BaseMailboxSerializer",
    "CorrespondentEmailSerializer",
    "CorrespondentSerializer",
    "DatabaseStatsSerializer",
    "EmailCorrespondentSerializer",
    "EmailSerializer",
    "FullEmailSerializer",
    "MailboxWithDaemonSerializer",
]
