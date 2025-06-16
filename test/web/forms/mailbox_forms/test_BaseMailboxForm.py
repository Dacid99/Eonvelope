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

"""Test module for the :class:`web.forms.BaseMailboxForm` form class."""

import pytest
from django.forms.models import model_to_dict

from web.forms import BaseMailboxForm


@pytest.mark.django_db
def test_post(mailbox_payload):
    """Tests post direction of :class:`web.forms.BaseMailboxForm`."""
    form = BaseMailboxForm(data=mailbox_payload)

    assert form.is_valid()
    form_data = form.cleaned_data
    assert "save_to_eml" in form_data
    assert form_data["save_to_eml"] == mailbox_payload["save_to_eml"]
    assert "save_attachments" in form_data
    assert form_data["save_attachments"] == mailbox_payload["save_attachments"]
    assert "is_favorite" in form_data
    assert form_data["is_favorite"] == mailbox_payload["is_favorite"]
    assert "name" not in form_data
    assert "account" not in form_data
    assert "is_healthy" not in form_data
    assert "created" not in form_data
    assert "updated" not in form_data
    assert len(form_data) == 3


@pytest.mark.django_db
def test_get(fake_mailbox):
    """Tests get direction of :class:`web.forms.BaseMailboxForm`."""
    form = BaseMailboxForm(instance=fake_mailbox)
    form_initial_data = form.initial
    form_fields = form.fields

    assert "save_to_eml" in form_fields
    assert "save_to_eml" in form_initial_data
    assert form_initial_data["save_to_eml"] == fake_mailbox.save_to_eml
    assert "save_attachments" in form_fields
    assert "save_attachments" in form_initial_data
    assert form_initial_data["save_attachments"] == fake_mailbox.save_attachments
    assert "is_favorite" in form_fields
    assert "is_favorite" in form_initial_data
    assert form_initial_data["is_favorite"] == fake_mailbox.is_favorite
    assert "name" not in form_fields
    assert "account" not in form_fields
    assert "is_healthy" not in form_fields
    assert "created" not in form_fields
    assert "updated" not in form_fields
    assert len(form_fields) == 3
