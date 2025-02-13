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

from django.db import models

from core.constants import HeaderFields

from .CorrespondentModel import CorrespondentModel


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
    """The correspondent that was mentioned in :attr:`email`. Unique together with :attr:`email` and :attr:`mention`."""

    MENTIONTYPES = list(HeaderFields.Correspondents())
    """The available types of correspondent memtions. Refers to :attr:`Emailkasten.constants.HeaderFields.Correspondents`."""

    mention = models.CharField(choices=MENTIONTYPES, max_length=30)
    """The way that :attr:`correspondent` was mentioned in :attr:`email`. One of :attr:`MENTIONTYPES`.  Unique together with :attr:`email` and :attr:`correspondent`."""

    created = models.DateTimeField(auto_now_add=True)
    """The datetime this entry was created. Is set automatically."""

    updated = models.DateTimeField(auto_now=True)
    """The datetime this entry was last updated. Is set automatically."""

    def __str__(self):
        return f"EMail-Correspondent connection from email {self.email} to correspondent {self.correspondent} with mention {self.mention}"

    class Meta:
        """Metadata class for the model."""

        db_table = "email_correspondents"
        """The name of the database bridge table for the emails and correspondents."""

        constraints = [
            models.UniqueConstraint(
                fields=["email", "correspondent", "mention"],
                name="emailcorrespondents_unique_together_email_correspondent_mention",
            )
        ]
        """:attr:`email`, :attr:`correspondent` and :attr:`mention` in combination are unique."""

    @staticmethod
    def fromHeader(
        header: str, headerName: str, email
    ) -> EMailCorrespondentsModel | None:
        new_correspondent = CorrespondentModel.fromHeader(header)
        if not new_correspondent:
            return None
        new_emailCorrespondent = EMailCorrespondentsModel(
            correspondent=new_correspondent, email=email, mention=headerName
        )
        return new_emailCorrespondent
