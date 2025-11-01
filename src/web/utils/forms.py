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

"""Module with custom form classes."""

from typing import Any

from django.forms import Form, ModelForm
from django.utils.translation import gettext_lazy as _


class RequiredMarkerModelForm(ModelForm):
    """A slightly extended version of :class:`django.forms.ModelForm` that adds a marker to required fields."""

    required_marker = _(" *")

    def __init__(self, *args: Any, **kwargs: Any):
        """Extended constructor adding :attr:`required_marker` to the required field labels."""
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            if self.fields[field_name].required:
                if self.fields[field_name].label is not None:
                    self.fields[field_name].label += self.required_marker  # type: ignore[operator]  #  adding StrPromises is fine
                else:
                    self.fields[field_name].label = self.required_marker


class RequiredMarkerForm(Form):
    """A slightly extended version of :class:`django.forms.Form` that adds a marker to required fields."""

    required_marker = _(" *")

    def __init__(self, *args: Any, **kwargs: Any):
        """Extended constructor adding :attr:`required_marker` to the required field labels."""
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            if self.fields[field_name].required:
                if self.fields[field_name].label is not None:
                    self.fields[field_name].label += self.required_marker  # type: ignore[operator]  #  adding StrPromises is fine
                else:
                    self.fields[field_name].label = self.required_marker
