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

"""Test module for the :class:`web.forms.BaseAccountForm` form class."""

import pytest
from django.forms.models import model_to_dict

from web.forms import BaseAccountForm


@pytest.mark.django_db
def test_post_create(fake_account, other_user):
    """Tests post direction of :class:`web.forms.BaseAccountForm`."""
    form = BaseAccountForm(data=model_to_dict(fake_account))
    form.instance.user = other_user

    assert form.is_valid()
    form_data = form.cleaned_data
    assert "mail_address" in form_data
    assert form_data["mail_address"] == fake_account.mail_address
    assert "password" in form_data
    assert form_data["password"] == fake_account.password
    assert "mail_host" in form_data
    assert form_data["mail_host"] == fake_account.mail_host
    assert "protocol" in form_data
    assert form_data["protocol"] == fake_account.protocol
    assert "mail_host_port" in form_data
    assert form_data["mail_host_port"] == fake_account.mail_host_port
    assert "timeout" in form_data
    assert form_data["timeout"] == fake_account.timeout
    assert "is_favorite" in form_data
    assert form_data["is_favorite"] == fake_account.is_favorite
    assert "user" not in form_data
    assert "is_healthy" not in form_data
    assert "created" not in form_data
    assert "updated" not in form_data
    assert len(form_data) == 7


@pytest.mark.django_db
def test_post_update(fake_account):
    """Tests post direction of :class:`web.forms.BaseAccountForm`."""
    form = BaseAccountForm(instance=fake_account, data=model_to_dict(fake_account))

    assert form.is_valid()
    form_data = form.cleaned_data
    assert "mail_address" in form_data
    assert form_data["mail_address"] == fake_account.mail_address
    assert "password" in form_data
    assert form_data["password"] == fake_account.password
    assert "mail_host" in form_data
    assert form_data["mail_host"] == fake_account.mail_host
    assert "protocol" in form_data
    assert form_data["protocol"] == fake_account.protocol
    assert "mail_host_port" in form_data
    assert form_data["mail_host_port"] == fake_account.mail_host_port
    assert "timeout" in form_data
    assert form_data["timeout"] == fake_account.timeout
    assert "is_favorite" in form_data
    assert form_data["is_favorite"] == fake_account.is_favorite
    assert "user" not in form_data
    assert "is_healthy" not in form_data
    assert "created" not in form_data
    assert "updated" not in form_data
    assert len(form_data) == 7


@pytest.mark.django_db
def test_get(fake_account):
    """Tests get direction of :class:`web.forms.BaseAccountForm`."""
    form = BaseAccountForm(instance=fake_account)
    form_initial_data = form.initial
    form_fields = form.fields

    assert "mail_address" in form_fields
    assert "mail_address" in form_initial_data
    assert form_initial_data["mail_address"] == fake_account.mail_address
    assert "password" in form_fields
    assert "password" in form_initial_data
    assert form_initial_data["mail_address"] == fake_account.mail_address
    assert "mail_host" in form_fields
    assert "mail_host" in form_initial_data
    assert form_initial_data["mail_host"] == fake_account.mail_host
    assert "protocol" in form_fields
    assert "protocol" in form_initial_data
    assert form_initial_data["protocol"] == fake_account.protocol
    assert "mail_host_port" in form_fields
    assert "mail_host_port" in form_initial_data
    assert form_initial_data["mail_host_port"] == fake_account.mail_host_port
    assert "timeout" in form_fields
    assert "timeout" in form_initial_data
    assert form_initial_data["timeout"] == fake_account.timeout
    assert "is_favorite" in form_fields
    assert "is_favorite" in form_initial_data
    assert form_initial_data["is_favorite"] == fake_account.is_favorite
    assert "user" not in form_fields
    assert "is_healthy" not in form_fields
    assert "created" not in form_fields
    assert "updated" not in form_fields
    assert len(form_fields) == 7
