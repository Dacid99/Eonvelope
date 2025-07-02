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

"""Module with the :class:`Correspondent` model class."""

from __future__ import annotations

import logging
from typing import override

from django.db import models
from django.utils.translation import gettext_lazy as _

from ..mixins import FavoriteMixin, URLMixin


logger = logging.getLogger(__name__)
"""The logger instance for the module."""


class Correspondent(URLMixin, FavoriteMixin, models.Model):
    """Database model for the correspondent data found in a mail."""

    email_name = models.TextField(
        default="",
        blank=True,
        verbose_name=_("mailer name"),
        help_text=_("The mailer name of the correspondent."),
    )
    """The mailer name. Can be blank if none has been found."""

    email_address = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("email address"),
    )
    """The mail address of the correspondent. Unique."""

    list_id = models.TextField(
        blank=True,
        default="",
        verbose_name=_("list ID"),
    )
    """The List-ID header of the mailinglist. Unique together with :attr:`correspondent`."""

    list_owner = models.TextField(
        blank=True,
        default="",
        verbose_name=_("list owner"),
    )
    """The List-Owner header of the mailinglist. Can be blank."""

    list_subscribe = models.TextField(
        blank=True,
        default="",
        verbose_name=_("list subscribe"),
    )
    """The List-Subscribe header of the mailinglist. Can be blank."""

    list_unsubscribe = models.TextField(
        blank=True,
        default="",
        verbose_name=_("list unsubscribe"),
    )
    """The List-Unsubscribe header of the mailinglist. Can be blank."""

    list_post = models.TextField(
        blank=True,
        default="",
        verbose_name=_("list post"),
    )
    """The List-Post header of the mailinglist. Can be blank."""

    list_help = models.TextField(
        blank=True,
        default="",
        verbose_name=_("list help"),
    )
    """The List-Help header of the mailinglist. Can be blank."""

    list_archive = models.TextField(
        blank=True,
        default="",
        verbose_name=_("list archive"),
    )
    """The List-Archive header of the mailinglist. Can be blank."""

    is_favorite = models.BooleanField(
        default=False,
        verbose_name=_("favorite"),
    )
    """Flags favorite correspondents. False by default."""

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("created"),
    )
    """The datetime this entry was created. Is set automatically."""

    updated = models.DateTimeField(
        auto_now=True,
        verbose_name=_("last updated"),
    )
    """The datetime this entry was last updated. Is set automatically."""

    BASENAME = "correspondent"

    DELETE_NOTICE = _("This will only delete this correspondent, not its emails.")

    class Meta:
        """Metadata class for the model."""

        db_table = "correspondents"
        """The name of the database table for the correspondents."""

    @override
    def __str__(self) -> str:
        """Returns a string representation of the model data.

        Returns:
            The string representation of the correspondent, using :attr:`email_address`.
        """
        return _("Correspondent with address %(email_address)s") % {
            "email_address": self.email_address
        }

    def is_mailinglist(self) -> bool:
        """Whether the correspondent is a mailinglist.

        Returns:
            Whether the correspondent has any list_ attributes.
        """
        return bool(
            self.list_id
            or self.list_archive
            or self.list_help
            or self.list_owner
            or self.list_post
            or self.list_subscribe
            or self.list_unsubscribe
        )

    @classmethod
    def create_from_correspondent_tuple(
        cls, correspondent_tuple: tuple[str, str]
    ) -> Correspondent | None:
        """Creates a :class:`core.models.Correspondent` from email header data.

        Args:
            correspondent_tuple: The tuple of correspondent data to create a model from.
            user: The user the correspondent shall belong to.

        Returns:
            The :class:`core.models.Correspondent` with the data from the header.
            If the correspondent already exists in the db returns that version.
            `None` if there is no address in :attr:`correspondent_tuple`.
        """
        name, address = correspondent_tuple
        if not address:
            logger.debug(
                "Skipping correspondent %s with empty mailaddress.",
                name,
            )
            return None
        try:
            correspondent = cls.objects.get(email_address=address)
        except cls.DoesNotExist:
            correspondent = cls(email_address=address, email_name=name)
            correspondent.save()
        return correspondent
