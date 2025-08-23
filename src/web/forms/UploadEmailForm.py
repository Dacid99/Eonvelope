# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Emailkasten Contributors
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

"""Module with the :class:`UploadEmailForm` form class."""

from django import forms
from django.utils.translation import gettext_lazy as _

from core.constants import SupportedEmailUploadFormats

from ..utils.forms import RequiredMarkerForm


class UploadEmailForm(RequiredMarkerForm):
    """Form for email file upload."""

    file_format = forms.ChoiceField(
        choices=SupportedEmailUploadFormats.choices,
        required=True,
        label=_("File format"),
        help_text=_("Select the format of the email file you want to upload."),
        localize=True,
    )
    file = forms.FileField(
        required=True,
        label=_("Email or Mailbox file"),
        help_text=_("Pick a file for upload."),
        localize=True,
    )
