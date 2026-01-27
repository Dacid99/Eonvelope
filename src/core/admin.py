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

"""The admin module for :mod:`core`. Registers all models and import-export resources with the admin."""

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export.resources import modelresource_factory

from .models import (
    Account,
    Attachment,
    Correspondent,
    Daemon,
    Email,
    EmailCorrespondent,
    Mailbox,
    StorageShard,
)

admin.site.register([StorageShard])

AccountResource = modelresource_factory(model=Account)
AttachmentResource = modelresource_factory(model=Attachment)
CorrespondentResource = modelresource_factory(model=Correspondent)
DaemonResource = modelresource_factory(model=Daemon)
EmailResource = modelresource_factory(model=Email)
EmailCorrespondentResource = modelresource_factory(model=EmailCorrespondent)
MailboxResource = modelresource_factory(model=Mailbox)


@admin.register(Account)
class AccountAdmin(ImportExportModelAdmin):
    """Admin config for :class:`core.models.Account`."""

    resource_classes = [AccountResource]


@admin.register(Attachment)
class AttachmentAdmin(ImportExportModelAdmin):
    """Admin config for :class:`core.models.Attachment`."""

    resource_classes = [AttachmentResource]


@admin.register(Correspondent)
class CorrespondentAdmin(ImportExportModelAdmin):
    """Admin config for :class:`core.models.Correspondent`."""

    resource_classes = [CorrespondentResource]


@admin.register(Daemon)
class DaemonAdmin(ImportExportModelAdmin):
    """Admin config for :class:`core.models.Daemon`."""

    resource_classes = [DaemonResource]


@admin.register(Email)
class EmailAdmin(ImportExportModelAdmin):
    """Admin config for :class:`core.models.Email`."""

    resource_classes = [EmailResource]


@admin.register(EmailCorrespondent)
class EmailCorrespondentAdmin(ImportExportModelAdmin):
    """Admin config for :class:`core.models.EmailCorrespondent`."""

    resource_classes = [EmailCorrespondentResource]


@admin.register(Mailbox)
class MailboxAdmin(ImportExportModelAdmin):
    """Admin config for :class:`core.models.Mailbox`."""

    resource_classes = [MailboxResource]
