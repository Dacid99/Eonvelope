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

"""Test module for the :class:`web.forms.BaseCorrespondentForm` form class."""

import pytest

from web.forms import BaseCorrespondentForm


@pytest.mark.django_db
def test_post(correspondent_payload):
    """Tests post direction of :class:`web.forms.BaseCorrespondentForm`."""
    form = BaseCorrespondentForm(data=correspondent_payload)

    assert form.is_valid()
    form_data = form.cleaned_data
    assert "real_name" in form_data
    assert form_data["real_name"] == correspondent_payload["real_name"]
    assert "is_favorite" in form_data
    assert form_data["is_favorite"] == correspondent_payload["is_favorite"]
    assert "email_address" not in form_data
    assert "created" not in form_data
    assert "updated" not in form_data
    assert len(form_data) == 2


@pytest.mark.django_db
def test_get(fake_correspondent):
    """Tests get direction of :class:`web.forms.BaseCorrespondentForm`."""
    form = BaseCorrespondentForm(instance=fake_correspondent)
    form_initial_data = form.initial
    form_fields = form.fields

    assert "real_name" in form_fields
    assert "real_name" in form_initial_data
    assert form_initial_data["real_name"] == fake_correspondent.email_name
    assert "is_favorite" in form_fields
    assert "is_favorite" in form_initial_data
    assert form_initial_data["is_favorite"] == fake_correspondent.is_favorite
    assert "email_address" not in form_fields
    assert "created" not in form_fields
    assert "updated" not in form_fields
    assert len(form_fields) == 2
