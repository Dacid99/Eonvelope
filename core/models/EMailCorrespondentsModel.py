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

"""Module with the :class:`EMailCorrespondentsModel` model class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final, override

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.constants import HeaderFields

from .CorrespondentModel import CorrespondentModel


if TYPE_CHECKING:
    from .EMailModel import EMailModel


class EMailCorrespondentsModel(models.Model):
    """Database model for connecting emails and their correspondents."""

    email = models.ForeignKey(
        "EMailModel", related_name="emailcorrespondents", on_delete=models.CASCADE
    )
    """The email :attr:`correspondent` was mentioned in. Unique together with :attr:`correspondent` and :attr:`mention`."""

    correspondent = models.ForeignKey(
        "CorrespondentModel",
        related_name="correspondentemails",
        on_delete=models.CASCADE,
    )
    """The correspondent mentioned in :attr:`email`. Unique together with :attr:`email` and :attr:`mention`."""

    mention = models.CharField(
        choices=HeaderFields.Correspondents.choices, max_length=30
    )
    """The mention of :attr:`correspondent` in :attr:`email`. Unique together with :attr:`email` and :attr:`correspondent`."""

    created = models.DateTimeField(auto_now_add=True)
    """The datetime this entry was created. Is set automatically."""

    updated = models.DateTimeField(auto_now=True)
    """The datetime this entry was last updated. Is set automatically."""

    class Meta:
        """Metadata class for the model."""

        db_table = "email_correspondents"
        """The name of the database bridge table for emails and correspondents."""

        constraints: Final[list[models.BaseConstraint]] = [
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
            "EMail-Correspondent connection from email %(email)s to correspondent %(correspondent)s with mention %(mention)s"
        ) % {
            "email": self.email,
            "correspondent": self.correspondent,
            "mention": self.mention,
        }

    @staticmethod
    def createFromHeader(
        header: str, headerName: str, email: EMailModel
    ) -> EMailCorrespondentsModel | None:
        """Prepares a :class:`core.models.EMailCorrespondentsModel.EMailCorrespondentsModel` from an email header.

        Args:
            header: The header to parse the malinglistdata from.
            headerName: The name of the header, the mention type of the correspondent.
            email: The email for the new emailcorrespondent.

        Returns:
            The :class:`core.models.EMailCorrespondentsModel.EMailCorrespondentsModel` instance with data from the header.
            If the correspondent already exists in the db uses that version.
            None if the correspondent could not be parsed.
        """
        if email.pk is None:
            raise ValueError("Email is not in the db!")
        new_correspondent = CorrespondentModel.fromHeader(header)
        if new_correspondent is None:
            return None
        new_correspondent.save()
        new_emailCorrespondent = EMailCorrespondentsModel(
            correspondent=new_correspondent, email=email, mention=headerName
        )
        new_emailCorrespondent.save()
        return new_emailCorrespondent
