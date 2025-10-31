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

"""Module with the adapted widget classes."""

from typing import Any

from django.forms import SelectDateWidget
from django.utils.translation import gettext as _


class AdaptedSelectDateWidget(SelectDateWidget):
    """Adapted version to fit the need of this project."""

    def __init__(self, **kwargs: Any):
        """Extended to ensure a default backward selection of years."""
        kwargs.pop("empty_label", None)
        super().__init__(
            empty_label=[
                f"--- {_('Year')} ---",
                f"--- {_('Month')} ---",
                f"--- {_('Day')} ---",
            ],
            **kwargs,
        )
        self.years = range(self.years.stop - 9, self.years.start - 9, -1)
