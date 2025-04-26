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

"""Test module for the :class:`web.forms.mailbox_forms.BaseMailboxForm.BaseMailboxForm` form class."""

import pytest
from django.forms.models import model_to_dict

from web.forms.mailbox_forms.BaseMailboxForm import BaseMailboxForm


@pytest.mark.django_db
def test_post(mailboxModel):
    """Tests post direction of :class:`web.forms.mailbox_forms.BaseMailboxForm.BaseMailboxForm`."""
    form = BaseMailboxForm(data=model_to_dict(mailboxModel))

    assert form.is_valid()
    form_data = form.cleaned_data
    assert "save_toEML" in form_data
    assert form_data["save_toEML"] == mailboxModel.save_toEML
    assert "save_toHTML" in form_data
    assert form_data["save_toHTML"] == mailboxModel.save_toHTML
    assert "save_attachments" in form_data
    assert form_data["save_attachments"] == mailboxModel.save_attachments
    assert "is_favorite" in form_data
    assert form_data["is_favorite"] == mailboxModel.is_favorite
    assert "name" not in form_data
    assert "account" not in form_data
    assert "is_healthy" not in form_data
    assert "created" not in form_data
    assert "updated" not in form_data
    assert len(form_data) == 4


@pytest.mark.django_db
def test_get(mailboxModel):
    """Tests get direction of :class:`web.forms.mailbox_forms.BaseMailboxForm.BaseMailboxForm`."""
    form = BaseMailboxForm(instance=mailboxModel)
    form_initial_data = form.initial
    form_fields = form.fields

    assert "save_toEML" in form_fields
    assert "save_toEML" in form_initial_data
    assert form_initial_data["save_toEML"] == mailboxModel.save_toEML
    assert "save_toHTML" in form_initial_data
    assert form_initial_data["save_toHTML"] == mailboxModel.save_toHTML
    assert "save_attachments" in form_fields
    assert "save_attachments" in form_initial_data
    assert form_initial_data["save_attachments"] == mailboxModel.save_attachments
    assert "is_favorite" in form_fields
    assert "is_favorite" in form_initial_data
    assert form_initial_data["is_favorite"] == mailboxModel.is_favorite
    assert "name" not in form_fields
    assert "account" not in form_fields
    assert "is_healthy" not in form_fields
    assert "created" not in form_fields
    assert "updated" not in form_fields
    assert len(form_fields) == 4
