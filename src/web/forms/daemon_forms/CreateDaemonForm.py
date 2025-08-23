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

"""Module with the :class:`BaseDaemonForm` form class."""

from __future__ import annotations

from typing import Any, ClassVar, override

from core.models import Mailbox
from web.forms.daemon_forms.BaseDaemonForm import BaseDaemonForm


class CreateDaemonForm(BaseDaemonForm):
    """Form for :class:`core.models.Daemon` which also allows to select a mailbox."""

    class Meta(BaseDaemonForm.Meta):
        """Metadata class form with a field for the mailbox fk."""

        fields: ClassVar[list[str]] = [*BaseDaemonForm.Meta.fields, "mailbox"]
        """Exposes all fields that the user should be able to change."""

    @override
    def __init__(self, *args: Any, **kwargs: Any):
        """Extended to restrict the choices for mailbox to the users mailboxes."""
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields["mailbox"].queryset = Mailbox.objects.filter(account__user=user)
        else:
            self.fields["mailbox"].queryset = Mailbox.objects.none()
