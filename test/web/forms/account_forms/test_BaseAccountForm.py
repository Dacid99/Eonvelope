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

"""Test module for the :class:`web.forms.BaseAccountForm` form class."""

import pytest
from django.forms import model_to_dict

from core.models import Account
from core.utils.fetchers.exceptions import MailAccountError
from web.forms import BaseAccountForm


@pytest.fixture(autouse=True)
def auto_mock_Account_test(mock_Account_test):
    """All tests mock Accounts test."""


@pytest.mark.django_db
def test_post_create_test_success(account_payload, other_user, mock_Account_test):
    """Tests post direction of :class:`web.forms.BaseAccountForm`."""
    form = BaseAccountForm(data=account_payload)
    form.instance.user = other_user

    assert form.is_valid()
    form_data = form.cleaned_data
    assert "mail_address" in form_data
    assert form_data["mail_address"] == account_payload["mail_address"]
    assert "password" in form_data
    assert form_data["password"] == account_payload["password"]
    assert "mail_host" in form_data
    assert form_data["mail_host"] == account_payload["mail_host"]
    assert "protocol" in form_data
    assert form_data["protocol"] == account_payload["protocol"]
    assert "mail_host_port" in form_data
    assert form_data["mail_host_port"] == account_payload["mail_host_port"]
    assert "timeout" in form_data
    assert form_data["timeout"] == account_payload["timeout"]
    assert "is_favorite" not in form_data
    assert "is_healthy" not in form_data
    assert "created" not in form_data
    assert "updated" not in form_data
    assert len(form_data) == 6
    mock_Account_test.assert_called_once()


@pytest.mark.django_db
def test_post_update_test_success(fake_account, account_payload, mock_Account_test):
    """Tests post direction of :class:`web.forms.BaseAccountForm`."""
    form = BaseAccountForm(instance=fake_account, data=account_payload)

    assert form.is_valid()
    form_data = form.cleaned_data
    assert "mail_address" in form_data
    assert form_data["mail_address"] == account_payload["mail_address"]
    assert "password" in form_data
    assert form_data["password"] == account_payload["password"]
    assert "mail_host" in form_data
    assert form_data["mail_host"] == account_payload["mail_host"]
    assert "protocol" in form_data
    assert form_data["protocol"] == account_payload["protocol"]
    assert "mail_host_port" in form_data
    assert form_data["mail_host_port"] == account_payload["mail_host_port"]
    assert "timeout" in form_data
    assert form_data["timeout"] == account_payload["timeout"]
    assert "is_favorite" not in form_data
    assert "is_healthy" not in form_data
    assert "created" not in form_data
    assert "updated" not in form_data
    assert len(form_data) == 6
    mock_Account_test.assert_called_once()


@pytest.mark.django_db
def test_post_create_test_failure(
    account_payload, other_user, fake_error_message, mock_Account_test
):
    """Tests post direction of :class:`web.forms.BaseAccountForm`."""
    mock_Account_test.side_effect = MailAccountError(ValueError(fake_error_message))

    form = BaseAccountForm(data=account_payload)
    form.instance.user = other_user

    assert not form.is_valid()
    assert len(form.errors) == 1
    assert "__all__" in form.errors
    assert len(form.errors["__all__"]) == 1
    assert fake_error_message in form.errors["__all__"][0]
    mock_Account_test.assert_called_once()
    assert len(mock_Account_test.call_args.kwargs) == 0
    assert len(mock_Account_test.call_args.args) == 1
    assert isinstance(mock_Account_test.call_args.args[0], Account)
    assert (
        mock_Account_test.call_args.args[0].mail_address
        == account_payload["mail_address"]
    )


@pytest.mark.django_db
def test_post_update_test_failure(
    fake_account, account_payload, fake_error_message, mock_Account_test
):
    """Tests post direction of :class:`web.forms.BaseAccountForm`."""
    mock_Account_test.side_effect = MailAccountError(ValueError(fake_error_message))

    form = BaseAccountForm(instance=fake_account, data=account_payload)

    assert not form.is_valid()
    assert len(form.errors) == 1
    assert "__all__" in form.errors
    assert len(form.errors["__all__"]) == 1
    assert fake_error_message in form.errors["__all__"][0]
    mock_Account_test.assert_called_once()
    assert len(mock_Account_test.call_args.kwargs) == 0
    assert len(mock_Account_test.call_args.args) == 1
    assert isinstance(mock_Account_test.call_args.args[0], Account)
    assert (
        mock_Account_test.call_args.args[0].mail_address
        == account_payload["mail_address"]
    )


@pytest.mark.django_db
def test_post_update_no_test(fake_account, mock_Account_test):
    """Tests post direction of :class:`web.forms.BaseAccountForm`."""
    unchanged_data = model_to_dict(fake_account)
    unchanged_data.pop("user")
    unchanged_data.pop("id")

    form = BaseAccountForm(instance=fake_account, data=unchanged_data)

    assert form.is_valid()
    mock_Account_test.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize("bad_mail_host_port", [-10, 98765])
def test_post_bad_mail_host_port(fake_account, account_payload, bad_mail_host_port):
    """Tests post direction of :class:`web.forms.BaseAccountForm`."""
    account_payload["mail_host_port"] = bad_mail_host_port

    form = BaseAccountForm(instance=fake_account, data=account_payload)

    assert not form.is_valid()
    assert form["mail_host_port"].errors


@pytest.mark.django_db
@pytest.mark.parametrize("bad_protocol", ["other"])
def test_post_bad_protocol(fake_account, account_payload, bad_protocol):
    """Tests post direction of :class:`web.forms.BaseAccountForm`."""
    account_payload["protocol"] = bad_protocol

    form = BaseAccountForm(instance=fake_account, data=account_payload)

    assert not form.is_valid()
    assert form["protocol"].errors


@pytest.mark.django_db
@pytest.mark.parametrize("bad_timeout", [-1])
def test_post_bad_timeout(fake_account, account_payload, bad_timeout):
    """Tests post direction of :class:`web.forms.BaseAccountForm`."""
    account_payload["timeout"] = bad_timeout

    form = BaseAccountForm(instance=fake_account, data=account_payload)

    assert not form.is_valid()
    assert form["timeout"].errors


@pytest.mark.django_db
def test_get(fake_account, mock_Account_test):
    """Tests get direction of :class:`web.forms.BaseAccountForm`."""
    form = BaseAccountForm(instance=fake_account)
    form_initial_data = form.initial
    form_fields = form.fields

    assert "mail_address" in form_fields
    assert "mail_address" in form_initial_data
    assert form_initial_data["mail_address"] == fake_account.mail_address
    assert "password" in form_fields
    assert "password" in form_initial_data
    assert form_initial_data["password"] == fake_account.password
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
    assert "is_favorite" not in form_fields
    assert "user" not in form_fields
    assert "is_healthy" not in form_fields
    assert "created" not in form_fields
    assert "updated" not in form_fields
    assert len(form_fields) == 6
    mock_Account_test.assert_not_called()


@pytest.mark.django_db
def test_save(other_user, account_payload, mock_Account_update_mailboxes):
    """Tests saving of :class:`web.forms.BaseAccountForm`."""
    form = BaseAccountForm(data=account_payload)
    form.instance.user = other_user

    assert Account.objects.count() == 0

    assert form.is_valid()
    form.save()

    assert Account.objects.count() == 1
    mock_Account_update_mailboxes.assert_called_once()
