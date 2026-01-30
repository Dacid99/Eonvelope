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

"""Module with the :class:`EmailCorrespondent` model class."""

from __future__ import annotations

from email.utils import getaddresses
from typing import TYPE_CHECKING, ClassVar, override

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin

from core.constants import HeaderFields
from core.mixins import TimestampModelMixin

from .Correspondent import Correspondent

if TYPE_CHECKING:
    from .Email import Email


class EmailCorrespondent(
    ExportModelOperationsMixin("email_correspondent"), TimestampModelMixin, models.Model
):
    """Database model for connecting emails and their correspondents."""

    email = models.ForeignKey(
        "Email",
        related_name="emailcorrespondents",
        on_delete=models.CASCADE,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("email"),
    )
    """The email :attr:`correspondent` was mentioned in. Unique together with :attr:`correspondent` and :attr:`mention`."""

    correspondent = models.ForeignKey(
        "Correspondent",
        related_name="correspondentemails",
        on_delete=models.CASCADE,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("correspondent"),
    )
    """The correspondent mentioned in :attr:`email`. Unique together with :attr:`email` and :attr:`mention`."""

    mention = models.CharField(
        choices=HeaderFields.Correspondents.choices,
        max_length=30,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("mention"),
    )
    """The mention of :attr:`correspondent` in :attr:`email`. Unique together with :attr:`email` and :attr:`correspondent`."""

    class Meta:
        """Metadata class for the model."""

        db_table = "email_correspondents"
        """The name of the database bridge table for emails and correspondents."""
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name = _("email-correspondents")
        get_latest_by = TimestampModelMixin.Meta.get_latest_by

        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["email", "correspondent", "mention"],
                name="emailcorrespondents_unique_together_email_correspondent_mention",
            ),
            models.CheckConstraint(
                condition=models.Q(mention__in=HeaderFields.Correspondents.values),
                name="mention_criterion_valid_choice",
            ),
        ]
        """:attr:`email`, :attr:`correspondent` and :attr:`mention` in combination are unique.
        Choices for :attr:`mention` are enforced on db level.
        """

    @override
    def __str__(self) -> str:
        """Returns a string representation of the model data.

        Returns:
            The string representation of the emailcorrespondent, using :attr:`email`, :attr:`correspondent` and :attr:`mention`.
        """
        return _(
            "Email-Correspondent connection from email %(email)s to correspondent %(correspondent)s with mention %(mention)s"
        ) % {
            "email": self.email,
            "correspondent": self.correspondent,
            "mention": self.mention,
        }

    @classmethod
    def create_from_header(
        cls, header: str, header_name: str, email: Email
    ) -> list[EmailCorrespondent] | None:
        """Prepares a list :class:`core.models.EmailCorrespondent` from an email header.

        Args:
            header: The header to parse the malinglistdata from.
            header_name: The name of the header, the mention type of the correspondent.
            email: The email for the new emailcorrespondent.

        Returns:
            The list of :class:`core.models.EmailCorrespondent` instances with data from the header.
            If the correspondent already exists in the db.
            `None` if the correspondent could not be parsed.

        Raises:
            ValueError: If the `email` argument is not in the db.
        """
        if email.pk is None:
            raise ValueError("Email is not in the db!")
        new_email_correspondent_models = []
        for correspondent_tuple in getaddresses([header]):
            correspondent = Correspondent.create_from_correspondent_tuple(
                correspondent_tuple, email.mailbox.account.user
            )
            if correspondent is None:
                continue
            new_email_correspondent = cls(
                correspondent=correspondent, email=email, mention=header_name
            )
            new_email_correspondent.save()
            new_email_correspondent_models.append(new_email_correspondent)
        return new_email_correspondent_models
