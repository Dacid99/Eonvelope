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

"""Module with the :class:`CorrespondentModel` model class."""

from __future__ import annotations

import logging

from django.db import models

from core.utils.mailParsing import parseCorrespondentHeader

logger = logging.getLogger(__name__)
"""The logger instance for the module."""


class CorrespondentModel(models.Model):
    """Database model for the correspondent data found in a mail."""

    email_name = models.CharField(max_length=255, blank=True)
    """The mailer name. Can be blank if none has been found."""

    email_address = models.CharField(max_length=255, unique=True)
    """The mail address of the correspondent. Unique."""

    is_favorite = models.BooleanField(default=False)
    """Flags favorite correspondents. False by default."""

    created = models.DateTimeField(auto_now_add=True)
    """The datetime this entry was created. Is set automatically."""

    updated = models.DateTimeField(auto_now=True)
    """The datetime this entry was last updated. Is set automatically."""

    def __str__(self):
        return f"Correspondent with address {self.email_address}"

    class Meta:
        """Metadata class for the model."""

        db_table = "correspondents"
        """The name of the database table for the correspondents."""

    @staticmethod
    def fromHeader(header: str) -> CorrespondentModel | None:
        """Prepares a :class:`core.models.CorrespondentModel.CorrespondentModel`
        from email header data.

        Args:
            header: The header to parse the correspondentdata from.

        Returns:
            The :class:`core.models.CorrespondentModel.CorrespondentModel` with the data from the header.
            If the correspondent already exists in the db returns that version.
            None if there is no address in :attr:`header`.
        """
        name, address = parseCorrespondentHeader(header)
        if not address:
            logger.debug(
                "Skipping correspondent with empty mailaddress %s.",
                address,
            )
            return None
        try:
            return CorrespondentModel.objects.get(email_address=address)
        except CorrespondentModel.DoesNotExist:
            pass

        return CorrespondentModel(email_address=address, email_name=name)
