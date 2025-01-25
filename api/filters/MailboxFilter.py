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

"""Module with the :class:`MailboxFilter` filter provider class."""

import django_filters

from Emailkasten.constants import FilterSetups
from core.models.MailboxModel import MailboxModel


class MailboxFilter(django_filters.FilterSet):
    """The filter class for :class:`core.models.MailboxModel`."""

    class Meta:
        """Metadata class for the filter."""

        model = MailboxModel
        fields = {
            "name": FilterSetups.TEXT,
            "save_toEML": FilterSetups.BOOL,
            "save_attachments": FilterSetups.BOOL,
            "save_images": FilterSetups.BOOL,
            "is_healthy": FilterSetups.BOOL,
            "is_favorite": FilterSetups.BOOL,
            "created": FilterSetups.DATETIME,
            "updated": FilterSetups.DATETIME,
            "account__mail_address": FilterSetups.TEXT,
            "account__mail_host": FilterSetups.TEXT,
            "account__protocol": FilterSetups.CHOICE,
            "account__is_healthy": FilterSetups.BOOL
        }
