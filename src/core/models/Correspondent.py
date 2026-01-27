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

"""Module with the :class:`Correspondent` model class."""

from __future__ import annotations

import logging
from io import BytesIO
from typing import TYPE_CHECKING, ClassVar, override

import httpcore
import httpx
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin
from rest_framework import status
from vobject import vCard

from core.mixins import (
    DownloadMixin,
    FavoriteModelMixin,
    TimestampModelMixin,
    URLMixin,
)
from core.utils.mail_parsing import find_best_href_in_header

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from django.db.models import QuerySet


logger = logging.getLogger(__name__)
"""The logger instance for the module."""


class Correspondent(
    ExportModelOperationsMixin("correspondent"),
    DownloadMixin,
    URLMixin,
    FavoriteModelMixin,
    TimestampModelMixin,
    models.Model,
):
    """Database model for the correspondent data found in a mail."""

    BASENAME = "correspondent"

    DELETE_NOTICE = _(
        "This will only delete the record of this correspondent, not of its emails."
    )

    DELETE_NOTICE_PLURAL = _(
        "This will only delete the records of these correspondents, not of their emails."
    )

    email_address = models.CharField(
        max_length=255,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("email address"),
    )
    """The mail address of the correspondent. Unique."""

    email_name = models.TextField(
        default="",
        blank=True,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("mailer name"),
        help_text=_("The mailer name of the correspondent."),
    )
    """The mailer name. Can be blank if none has been found."""

    real_name = models.CharField(
        max_length=255,
        default="",
        blank=True,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("real name"),
        help_text=_("The real name of the correspondent."),
    )
    """The real name. Can be blank if the user doesn't set one."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("user"),
        on_delete=models.CASCADE,
    )

    list_id = models.TextField(
        blank=True,
        default="",
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("list ID"),
    )
    """The List-ID header of the mailinglist. Unique together with :attr:`correspondent`."""

    list_owner = models.TextField(
        blank=True,
        default="",
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("list owner"),
    )
    """The List-Owner header of the mailinglist. Can be blank."""

    list_subscribe = models.TextField(
        blank=True,
        default="",
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("list-subscribe"),
    )
    """The List-Subscribe header of the mailinglist. Can be blank."""

    list_unsubscribe = models.TextField(
        blank=True,
        default="",
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("list-unsubscribe"),
    )
    """The List-Unsubscribe header of the mailinglist. Can be blank."""

    list_unsubscribe_post = models.CharField(
        max_length=255,
        blank=True,
        default="",
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("list-unsubscribe method"),
    )
    """The List-Unsubscribe-Post header of the mailinglist. Can be blank."""

    list_post = models.TextField(
        blank=True,
        default="",
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("list post"),
    )
    """The List-Post header of the mailinglist. Can be blank."""

    list_help = models.TextField(
        blank=True,
        default="",
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("list help"),
    )
    """The List-Help header of the mailinglist. Can be blank."""

    list_archive = models.TextField(
        blank=True,
        default="",
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("list archive"),
    )
    """The List-Archive header of the mailinglist. Can be blank."""

    class Meta:
        """Metadata class for the model."""

        db_table = "correspondents"
        """The name of the database table for the correspondents."""
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name = _("correspondent")
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name_plural = _("correspondents")
        get_latest_by = TimestampModelMixin.Meta.get_latest_by

        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["email_address", "user"],
                name="email_unique_together_email_address_user",
            )
        ]
        """:attr:`email_address` and :attr:`user` in combination are unique."""

    @override
    def __str__(self) -> str:
        """Returns a string representation of the model data.

        Returns:
            The string representation of the correspondent, using :attr:`email_address`.
        """
        return _("Correspondent with address %(email_address)s") % {
            "email_address": self.email_address
        }

    def share_to_nextcloud(self) -> None:
        """Sends this attachment to the Nextcloud server of its user.

        Note:
            Nextcloud returns 201 on success.

        Raises:
            RuntimeError: If the users Nextcloud URL is not or improperly set.
            ConnectionError: If connecting to Nextcloud failed.
            PermissionError: If authentication to Nextcloud failed.
            ValueError: If uploading the file to Nextcloud resulted in a bad response.
        """
        nextcloud_baseurl = self.user.profile.nextcloud_url.rstrip("/")
        logger.debug(
            "Sending %s to Nextcloud server at %s ...", str(self), nextcloud_baseurl
        )
        put_contact_url = (
            nextcloud_baseurl
            + "/remote.php/dav/addressbooks/users/"
            + f"{self.user.profile.nextcloud_username.lower()}/{self.user.profile.nextcloud_addressbook.lower()}/{self.id}_eonvelope.vcf"
        )
        headers = {
            "Depth": "0",
            "Content-Type": "text/vcard; charset=utf-8;",
            "DNT": "1",
        }
        auth = httpx.BasicAuth(
            username=self.user.profile.nextcloud_username,
            password=self.user.profile.nextcloud_password,
        )
        try:
            response = httpx.put(
                put_contact_url,
                headers=headers,
                content=Correspondent.queryset_as_file(
                    Correspondent.objects.filter(id=self.id)
                ),
                auth=auth,
            )
        except (
            httpcore.UnsupportedProtocol,
            httpx.UnsupportedProtocol,
            httpx.InvalidURL,
        ) as error:
            logger.info(
                "Failed to send attachment to Nextcloud.",
                exc_info=True,
            )
            raise RuntimeError(
                # Translators: Nextcloud is a brand name.
                _("Nextcloud URL is malformed: %(error)s")
                % {"error": error}
            ) from error
        except httpx.RequestError as error:
            logger.info("Failed to send attachment to Nextcloud.", exc_info=True)
            raise ConnectionError(
                # Translators: Nextcloud is a brand name.
                _("Error connecting to the Nextcloud server: %(error)s")
                % {"error": error}
            ) from error
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            logger.info("Failed to send attachment to Nextcloud.", exc_info=True)
            if error.response.status_code in [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ]:
                raise PermissionError(
                    # Translators: Nextcloud is a brand name.
                    _("Authentication to Nextcloud failed: %(response)s")
                    % {"response": error.response.text}
                ) from error
            raise ValueError(
                # Translators: Nextcloud is a brand name.
                _("Uploading to Nextcloud failed: %(response)s")
                % {"response": error.response.text}
            ) from error
        logger.debug("Successfully sent attachment to Nextcloud.")

    @property
    def is_mailinglist(self) -> bool:
        """Whether the correspondent is a mailinglist.

        Returns:
            Whether the correspondent has any `list_` attributes.
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

    @property
    def list_unsubscribe_post_name(self) -> str:
        """Gets the name of the list unsubscribe method from `list_unsubscribe`.

        Returns:
            The name of the list unsubscribe method.
        """
        return self.list_unsubscribe_post.removeprefix("List-Unsubscribe=")

    @property
    def list_archive_href(self) -> str:
        """Parses the href for subscribing to the correspondents list.

        Returns:
            The correspondents subscribe hyperref.
            The empty string if list_unsubscribe is empty.
        """
        return find_best_href_in_header(self.list_archive)

    @property
    def list_help_href(self) -> str:
        """Parses the href for subscribing to the correspondents list.

        Returns:
            The correspondents subscribe hyperref.
            The empty string if list_unsubscribe is empty.
        """
        return find_best_href_in_header(self.list_help)

    @property
    def list_post_href(self) -> str:
        """Parses the href for subscribing to the correspondents list.

        Returns:
            The correspondents subscribe hyperref.
            The empty string if list_unsubscribe is empty.
        """
        return find_best_href_in_header(self.list_post)

    @property
    def list_subscribe_href(self) -> str:
        """Parses the href for subscribing to the correspondents list.

        Returns:
            The correspondents subscribe hyperref.
            The empty string if list_unsubscribe is empty.
        """
        return find_best_href_in_header(self.list_subscribe)

    @property
    def list_unsubscribe_href(self) -> str:
        """Parses the href for unsubscribing from the correspondents list.

        Returns:
            The correspondents unsubscribe hyperref.
            The empty string if list_unsubscribe is empty.
        """
        return find_best_href_in_header(self.list_unsubscribe)

    @property
    def name(self) -> str:
        """Gets the best available name for the correspondent, if necessary from the mailaddress.

        Returns:
            The most accurate available name of the correspondent.
        """
        return self.real_name or self.email_name or self.email_address.split("@")[0]

    @property
    @override
    def has_download(self) -> bool:
        """Correspondent can always be downloaded."""
        return True

    @classmethod
    def create_from_correspondent_tuple(
        cls, correspondent_tuple: tuple[str, str], user: User
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
            correspondent = cls.objects.get(email_address=address.strip(), user=user)
            correspondent.email_name = name
            correspondent.save()
            logger.debug("Correspondent %s already exists in db.", address)
        except cls.DoesNotExist:
            correspondent = cls(
                email_address=address.strip(), email_name=name, user=user
            )
            correspondent.save()
            logger.debug("Successfully saved correspondent %s to db.", address)
        return correspondent

    @staticmethod
    def queryset_as_file(queryset: QuerySet) -> BytesIO:
        """Parse the correspondents in the queryset into a vcard object bytestream.

        Args:
            queryset: The correspondent queryset to compile into a file.

        Returns:
            The vcard object bytestream.

        Raises:
            Correspondent.DoesNotExist: If the :attr:`queryset` is empty.
        """
        if not queryset.exists():
            raise Correspondent.DoesNotExist("The queryset is empty!")
        vcard_buffer = BytesIO()
        for correspondent in queryset:
            correspondent_vcard = vCard()
            correspondent_vcard.add("email").value = correspondent.email_address
            correspondent_vcard.add("fn").value = correspondent.name
            correspondent_vcard.add("nickname").value = correspondent.email_name
            vcard_buffer.write(correspondent_vcard.serialize().encode())
        vcard_buffer.seek(0)
        return vcard_buffer
