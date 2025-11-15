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

"""Module with the :class:`UserProfile` model class."""

from typing import override

from django.conf import settings
from django.core.validators import URLValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserProfile(models.Model):
    """Database model for the profile data of a user."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        unique=True,
        editable=False,
    )
    paperless_url = models.URLField(
        default="",
        blank=True,
        max_length=255,
        validators=[URLValidator(schemes=["http", "https"])],
        # Translators: Do not capitalize the very first letter unless your language requires it. Paperless is a brand name.
        verbose_name=_("Paperless server URL"),
        # Translators: Paperless is a brand name.
        help_text=_("URL of your Paperless server."),
    )
    paperless_api_key = models.CharField(
        default="",
        blank=True,
        max_length=255,
        # Translators: Do not capitalize the very first letter unless your language requires it. Paperless is a brand name.
        verbose_name=_("Paperless server API key"),
        # Translators: Paperless is a brand name.
        help_text=_("API key for your Paperless server."),
    )
    paperless_tika_enabled = models.BooleanField(
        default=False,
        blank=True,
        # Translators: Do not capitalize the very first letter unless your language requires it. Paperless and Tika are brand names.
        verbose_name=_("Paperless Tika support enabled"),
        # Translators: Paperless and Tika are brand names.
        help_text=_("Whether Tika support is enabled on your Paperless server."),
    )
    immich_url = models.URLField(
        default="",
        blank=True,
        max_length=255,
        validators=[URLValidator(schemes=["http", "https"])],
        # Translators: Do not capitalize the very first letter unless your language requires it. Immich is a brand name.
        verbose_name=_("Immich server URL"),
        # Translators: Immich is a brand name.
        help_text=_("URL of your Immich server."),
    )
    immich_api_key = models.CharField(
        default="",
        blank=True,
        max_length=255,
        # Translators: Do not capitalize the very first letter unless your language requires it. Immich is a brand name.
        verbose_name=_("Immich server API key"),
        # Translators: Immich is a brand name.
        help_text=_("API key for your Immich server."),
    )
    nextcloud_url = models.URLField(
        default="",
        blank=True,
        max_length=255,
        validators=[URLValidator(schemes=["http", "https"])],
        # Translators: Do not capitalize the very first letter unless your language requires it. Nextcloud is a brand name.
        verbose_name=_("Nextcloud server URL"),
        # Translators: Nextcloud is a brand name.
        help_text=_("URL of your Nextcloud server."),
    )
    nextcloud_username = models.CharField(
        default="",
        blank=True,
        max_length=255,
        # Translators: Do not capitalize the very first letter unless your language requires it. Nextcloud is a brand name.
        verbose_name=_("Nextcloud server username"),
        # Translators: Nextcloud is a brand name.
        help_text=_("Username for your Nextcloud account."),
    )
    nextcloud_password = models.CharField(
        default="",
        blank=True,
        max_length=255,
        # Translators: Do not capitalize the very first letter unless your language requires it. Nextcloud is a brand name.
        verbose_name=_("Nextcloud server password"),
        # Translators: Nextcloud is a brand name.
        help_text=_("Password for your Nextcloud account."),
    )
    nextcloud_addressbook = models.CharField(
        default="contacts",
        blank=True,
        max_length=255,
        # Translators: Do not capitalize the very first letter unless your language requires it. Nextcloud is a brand name.
        verbose_name=_("Nextcloud server addressbook"),
        # Translators: Nextcloud is a brand name.
        help_text=_("Main addressbook of your Nextcloud account."),
    )

    class Meta:
        """Metadata class for the model."""

        db_table = "user_profiles"
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name = _("user profile")
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name_plural = _("user profiles")

    @override
    def __str__(self) -> str:
        """Returns a string representation of the model data.

        Returns:
            The string representation of the profile, using :attr:`user`.
        """
        return _("Profile for user %(username)s ") % {
            "username": self.user.username,
        }
