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

"""Module with the :class:`MailingListModel` model class."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, override

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.mixins.FavoriteMixin import FavoriteMixin
from core.mixins.URLMixin import URLMixin

from ..constants import HeaderFields
from ..utils.mailParsing import getHeader


if TYPE_CHECKING:
    from email.message import EmailMessage


logger = logging.getLogger(__name__)


class MailingListModel(URLMixin, FavoriteMixin, models.Model):
    """Database model for a mailinglist."""

    list_id = models.CharField(max_length=255, unique=True)
    """The List-ID header of the mailinglist. Unique together with :attr:`correspondent`."""

    list_owner = models.CharField(max_length=255, blank=True, default="")
    """The List-Owner header of the mailinglist. Can be blank."""

    list_subscribe = models.EmailField(max_length=255, blank=True, default="")
    """The List-Subscribe header of the mailinglist. Can be blank."""

    list_unsubscribe = models.EmailField(max_length=255, blank=True, default="")
    """The List-Unsubscribe header of the mailinglist. Can be blank."""

    list_post = models.CharField(max_length=255, blank=True, default="")
    """The List-Post header of the mailinglist. Can be blank."""

    list_help = models.CharField(max_length=255, blank=True, default="")
    """The List-Help header of the mailinglist. Can be blank."""

    list_archive = models.CharField(max_length=255, blank=True, default="")
    """The List-Archive header of the mailinglist. Can be blank."""

    is_favorite = models.BooleanField(default=False)
    """Flags favorite mailingslists. False by default."""

    created = models.DateTimeField(auto_now_add=True)
    """The datetime this entry was created. Is set automatically."""

    updated = models.DateTimeField(auto_now=True)
    """The datetime this entry was last updated. Is set automatically."""

    BASENAME = "mailinglist"

    DELETE_NOTICE = _("This will delete this mailinglist and all its emails!")

    class Meta:
        """Metadata class for the model."""

        db_table = "mailinglists"
        """The name of the database table for the mailinglists."""

    @override
    def __str__(self) -> str:
        """Returns a string representation of the model data.

        Returns:
            The string representation of the mailinglist, using :attr:`list_id`.
        """
        return _("Mailinglist %(list_id)s from %(list_owner)s") % {
            "list_id": self.list_id,
            "list_owner": self.list_owner,
        }

    @staticmethod
    def fromEmailMessage(emailMessage: EmailMessage) -> MailingListModel | None:
        """Prepares a :class:`core.models.MailingListModel.MailingListModel` from an email message.

        Args:
            emailMessage: The email message to parse the malinglistdata from.

        Returns:
            The :class:`core.models.MailingListModel.MailingListModel` instance with data from the message.
            If the correspondent already exists in the db returns that version.
            None if there is no List-ID header in :attr:`emailMessage`.
        """
        list_id = getHeader(emailMessage, HeaderFields.MailingList.ID)
        if not list_id:
            logger.debug(
                "Skipping mailinglist with empty list id %s.",
                list_id,
            )
            return None
        try:
            return MailingListModel.objects.get(list_id=list_id)
        except MailingListModel.DoesNotExist:
            pass

        new_mailinglist = MailingListModel(list_id=list_id)
        new_mailinglist.list_owner = getHeader(
            emailMessage, HeaderFields.MailingList.OWNER, fallbackCallable=lambda: ""
        )
        new_mailinglist.list_subscribe = getHeader(
            emailMessage,
            HeaderFields.MailingList.SUBSCRIBE,
            fallbackCallable=lambda: "",
        )
        new_mailinglist.list_unsubscribe = getHeader(
            emailMessage,
            HeaderFields.MailingList.UNSUBSCRIBE,
            fallbackCallable=lambda: "",
        )
        new_mailinglist.list_post = getHeader(
            emailMessage, HeaderFields.MailingList.POST, fallbackCallable=lambda: ""
        )
        new_mailinglist.list_help = getHeader(
            emailMessage, HeaderFields.MailingList.HELP, fallbackCallable=lambda: ""
        )
        new_mailinglist.list_archive = getHeader(
            emailMessage, HeaderFields.MailingList.ARCHIVE, fallbackCallable=lambda: ""
        )
        return new_mailinglist
