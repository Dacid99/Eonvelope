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

"""Test module for :mod:`core.models.Correspondent`."""

from __future__ import annotations

import datetime

import httpx
import pytest
import vobject
from django.core.files.storage import default_storage
from django.db import IntegrityError
from django.urls import reverse
from model_bakery import baker

from core.models import Correspondent


@pytest.fixture
def fake_correspondent_tuple(faker):
    """Returns a fake correspondent tuple."""
    return (faker.name(), faker.email())


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    """The mocked :attr:`core.models.Correspondent.logger`."""
    return mocker.patch("core.models.Correspondent.logger", autospec=True)


@pytest.fixture
def mock_httpx_put(mocker, faker):
    """Fixture mocking the post method of :mod:`httpx`."""
    fake_response = httpx.Response(
        200,
        content=f'{{"{faker.word()}": "{faker.uuid4()}"}}',
        request=httpx.Request("put", faker.url()),
    )
    return mocker.patch("httpx.put", autospec=True, return_value=fake_response)


@pytest.mark.django_db
def test_Correspondent_fields(fake_correspondent):
    """Tests the fields of :class:`core.models.Correspondent.Correspondent`."""

    assert fake_correspondent.email_name is not None
    assert isinstance(fake_correspondent.email_name, str)
    assert fake_correspondent.email_address is not None
    assert isinstance(fake_correspondent.email_address, str)
    assert fake_correspondent.list_id is not None
    assert isinstance(fake_correspondent.list_id, str)
    assert fake_correspondent.list_owner is not None
    assert isinstance(fake_correspondent.list_owner, str)
    assert fake_correspondent.list_subscribe is not None
    assert isinstance(fake_correspondent.list_subscribe, str)
    assert fake_correspondent.list_unsubscribe is not None
    assert isinstance(fake_correspondent.list_unsubscribe, str)
    assert fake_correspondent.list_post is not None
    assert isinstance(fake_correspondent.list_post, str)
    assert fake_correspondent.list_help is not None
    assert isinstance(fake_correspondent.list_help, str)
    assert fake_correspondent.list_archive is not None
    assert isinstance(fake_correspondent.list_archive, str)
    assert fake_correspondent.is_favorite is False
    assert fake_correspondent.updated is not None
    assert isinstance(fake_correspondent.updated, datetime.datetime)
    assert fake_correspondent.created is not None
    assert isinstance(fake_correspondent.created, datetime.datetime)


@pytest.mark.django_db
def test_Correspondent___str__(fake_correspondent):
    """Tests the string representation of :class:`core.models.Correspondent.Correspondent`."""
    assert fake_correspondent.email_address in str(fake_correspondent)


@pytest.mark.django_db
def test_Correspondent_unique_together_constraint(fake_correspondent):
    """Tests the unique constraint in :class:`core.models.Correspondent.Correspondent`."""

    with pytest.raises(IntegrityError):
        baker.make(
            Correspondent,
            user=fake_correspondent.user,
            email_address=fake_correspondent.email_address,
        )


@pytest.mark.django_db
def test_Correspondent_share_to_nextcloud_success(
    faker, fake_correspondent, mock_logger, mock_httpx_put
):
    """Tests :func:`core.models.Correspondent.Correspondent.share_to_nextcloud`
    in case of success.
    """
    profile = fake_correspondent.user.profile
    profile.nextcloud_url = faker.url()
    profile.nextcloud_api_key = faker.word()
    profile.save()

    result = fake_correspondent.share_to_nextcloud()

    assert not result
    mock_httpx_put.assert_called_once()
    assert (
        mock_httpx_put.call_args.args[0]
        == profile.nextcloud_url.strip("/")
        + "/remote.php/dav/addressbooks/users/"
        + f"{profile.nextcloud_username.lower()}/{profile.nextcloud_addressbook.lower()}/{fake_correspondent.id}_emailkasten.vcf"
    )
    assert mock_httpx_put.call_args.kwargs["headers"] == {
        "Depth": "0",
        "Content-Type": "text/vcard; charset=utf-8;",
        "DNT": "1",
    }
    assert (
        mock_httpx_put.call_args.kwargs["content"].read()
        == Correspondent.queryset_as_file(
            Correspondent.objects.filter(id=fake_correspondent.id)
        ).read()
    )
    assert (
        mock_httpx_put.call_args.kwargs["auth"]._auth_header
        == httpx.BasicAuth(
            username=profile.nextcloud_username,
            password=profile.nextcloud_password,
        )._auth_header
    )
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_Correspondent_share_to_nextcloud_no_password(
    faker, fake_correspondent, mock_logger, mock_httpx_put
):
    """Tests :func:`core.models.Correspondent.Correspondent.share_to_nextcloud`
    in case there is no apikey.
    This test makes sure there is no error constructing the header.
    """
    fake_correspondent.user.profile.nextcloud_url = faker.url()
    fake_correspondent.user.profile.save()
    mock_httpx_put.return_value.status_code = 401

    with pytest.raises(PermissionError):
        fake_correspondent.share_to_nextcloud()

    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize("nextcloud_url", ["test.org", "smb://100.200.051.421", ""])
def test_Correspondent_share_to_nextcloud_error_request_setup(
    fake_correspondent, mock_logger, nextcloud_url
):
    """Tests :func:`core.models.Correspondent.Correspondent.share_to_nextcloud`
    in case of an error with the request.
    """
    fake_correspondent.user.profile.nextcloud_url = nextcloud_url
    fake_correspondent.user.profile.save()

    with pytest.raises(RuntimeError):
        fake_correspondent.share_to_nextcloud()

    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_Correspondent_share_to_nextcloud_error_request(
    fake_error_message,
    fake_correspondent,
    mock_logger,
    mock_httpx_put,
):
    """Tests :func:`core.models.Correspondent.Correspondent.share_to_nextcloud`
    in case of an error with the request.
    """
    mock_httpx_put.side_effect = httpx.RequestError(fake_error_message)

    with pytest.raises(ConnectionError, match=fake_error_message):
        fake_correspondent.share_to_nextcloud()

    mock_httpx_put.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize("status_code", [401, 403])
def test_Correspondent_share_to_nextcloud_unauthorized(
    fake_error_message,
    fake_correspondent,
    mock_httpx_put,
    mock_logger,
    status_code,
):
    """Tests :func:`core.models.Correspondent.Correspondent.share_to_nextcloud`
    in case of an error authenticating.
    """
    mock_httpx_put.return_value = httpx.Response(
        status_code,
        content=f'{{"detail": "{fake_error_message}"}}',
        request=mock_httpx_put.return_value.request,
    )

    with pytest.raises(PermissionError, match=fake_error_message):
        fake_correspondent.share_to_nextcloud()

    mock_httpx_put.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize("status_code", [400, 500, 300])
def test_Correspondent_share_to_nextcloud_error_status(
    fake_error_message,
    fake_correspondent,
    mock_httpx_put,
    mock_logger,
    status_code,
):
    """Tests :func:`core.models.Correspondent.Correspondent.share_to_nextcloud`
    in case of a bad status response.
    """
    mock_httpx_put.return_value = httpx.Response(
        status_code,
        content=f'{{"detail": "{fake_error_message}"}}',
        request=mock_httpx_put.return_value.request,
    )

    with pytest.raises(ValueError, match=fake_error_message):
        fake_correspondent.share_to_nextcloud()

    mock_httpx_put.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "email_name, real_name, email_address, expected_name",
    [
        ("", "", "abc113@web.ca", "abc113"),
        ("john doe", "", "jd@mail.it", "john doe"),
        ("", "dudeonline", "lol@somewhere.io", "dudeonline"),
        ("mailer", "real", "email@address.us", "real"),
    ],
)
def test_Correspondent_name(
    fake_correspondent, email_name, real_name, email_address, expected_name
):
    """Tests :func:`core.models.Correspondent.Correspondent.name`
    for different cases of email- real_name, email_address combinations.
    """
    fake_correspondent.email_name = email_name
    fake_correspondent.real_name = real_name
    fake_correspondent.email_address = email_address

    result = fake_correspondent.name

    assert result == expected_name


@pytest.mark.django_db
def test_Correspondent_queryset_as_file(fake_correspondent):
    """Tests :func:`core.models.Correspondent.Correspondent.queryset_as_file`
    in case of success.
    """
    result = Correspondent.queryset_as_file(Correspondent.objects.all())

    assert hasattr(result, "read")
    for correspondent_vcard in vobject.readComponents(result.read().decode()):
        correspondent_vcard.fn = fake_correspondent.name
        correspondent_vcard.email = fake_correspondent.email_address
    assert hasattr(result, "close")
    result.close()


@pytest.mark.django_db
def test_Correspondent_create_from_correspondent_tuple_success(
    fake_correspondent_tuple, owner_user
):
    """Tests :func:`core.models.Correspondent.Correspondent.create_from_correspondent_tuple`
    in case of success.
    """
    assert Correspondent.objects.count() == 0

    result = Correspondent.create_from_correspondent_tuple(
        fake_correspondent_tuple, owner_user
    )

    assert isinstance(result, Correspondent)
    assert result.pk is not None
    assert result.user == owner_user
    assert Correspondent.objects.count() == 1
    assert result.email_name == fake_correspondent_tuple[0]
    assert result.email_address == fake_correspondent_tuple[1]


@pytest.mark.django_db
def test_Correspondent_create_from_correspondent_tuple_success_unstripped_address(
    fake_correspondent_tuple, owner_user
):
    """Tests :func:`core.models.Correspondent.Correspondent.create_from_correspondent_tuple`
    in case of success.
    """
    fake_correspondent_tuple = (
        fake_correspondent_tuple[0],
        " " + fake_correspondent_tuple[1] + " ",
    )
    assert Correspondent.objects.count() == 0

    result = Correspondent.create_from_correspondent_tuple(
        fake_correspondent_tuple, owner_user
    )

    assert isinstance(result, Correspondent)
    assert result.pk is not None
    assert result.user == owner_user
    assert Correspondent.objects.count() == 1
    assert result.email_name == fake_correspondent_tuple[0]
    assert result.email_address == fake_correspondent_tuple[1].strip()


@pytest.mark.django_db
def test_Correspondent_create_from_correspondent_tuple_duplicate(
    fake_correspondent, fake_correspondent_tuple
):
    """Tests :func:`core.models.Correspondent.Correspondent.create_from_correspondent_tuple`
    in case the correspondent to be prepared is already being in the database.
    """
    fake_correspondent_tuple = (
        fake_correspondent_tuple[0],
        fake_correspondent.email_address,
    )

    assert Correspondent.objects.count() == 1

    result = Correspondent.create_from_correspondent_tuple(
        fake_correspondent_tuple, user=fake_correspondent.user
    )

    assert result == fake_correspondent
    assert Correspondent.objects.count() == 1


@pytest.mark.django_db
def test_Correspondent_create_from_correspondent_tuple_no_address(
    mock_logger, fake_correspondent_tuple, owner_user
):
    """Tests :func:`core.models.Correspondent.Correspondent.create_from_correspondent_tuple`
    in case of there is no address in the header.
    """
    fake_correspondent_tuple = (fake_correspondent_tuple[0], "")

    assert Correspondent.objects.count() == 0

    result = Correspondent.create_from_correspondent_tuple(
        fake_correspondent_tuple, user=owner_user
    )

    assert result is None
    assert Correspondent.objects.count() == 0
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_Correspondent_get_absolute_url(fake_correspondent):
    """Tests :func:`core.models.Correspondent.Correspondent.get_absolute_url`."""
    result = fake_correspondent.get_absolute_url()

    assert result == reverse(
        f"web:{fake_correspondent.BASENAME}-detail",
        kwargs={"pk": fake_correspondent.pk},
    )


@pytest.mark.django_db
def test_Correspondent_get_absolute_edit_url(fake_correspondent):
    """Tests :func:`core.models.Correspondent.Correspondent.get_absolute_edit_url`."""
    result = fake_correspondent.get_absolute_edit_url()

    assert result == reverse(
        f"web:{fake_correspondent.BASENAME}-edit",
        kwargs={"pk": fake_correspondent.pk},
    )


@pytest.mark.django_db
def test_Correspondent_get_absolute_list_url(fake_correspondent):
    """Tests :func:`core.models.Correspondent.Correspondent.get_absolute_list_url`."""
    result = fake_correspondent.get_absolute_list_url()

    assert result == reverse(
        f"web:{fake_correspondent.BASENAME}-filter-list",
    )
