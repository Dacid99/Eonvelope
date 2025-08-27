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

"""Test module for :mod:`api.v1.views.CorrespondentViewSet`'s custom actions."""

from __future__ import annotations

import pytest
from django.http import FileResponse
from rest_framework import status

from api.v1.views import CorrespondentViewSet
from core.models import Correspondent


@pytest.fixture
def mock_Correspondent_queryset_as_file(mocker, fake_file):
    return mocker.patch(
        "api.v1.views.CorrespondentViewSet.Correspondent.queryset_as_file",
        return_value=fake_file,
    )


@pytest.mark.django_db
def test_download_noauth(
    fake_correspondent,
    noauth_api_client,
    custom_detail_action_url,
):
    """Tests the get method :func:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet.download` action
    with an unauthenticated user client.
    """
    response = noauth_api_client.get(
        custom_detail_action_url(
            CorrespondentViewSet,
            CorrespondentViewSet.URL_NAME_DOWNLOAD,
            fake_correspondent,
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not isinstance(response, FileResponse)


@pytest.mark.django_db
def test_download_auth_other(
    fake_correspondent,
    other_api_client,
    custom_detail_action_url,
):
    """Tests the get method :func:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet.download` action
    with the authenticated other user client.
    """
    response = other_api_client.get(
        custom_detail_action_url(
            CorrespondentViewSet,
            CorrespondentViewSet.URL_NAME_DOWNLOAD,
            fake_correspondent,
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert not isinstance(response, FileResponse)


@pytest.mark.django_db
def test_download_auth_owner(
    fake_correspondent,
    owner_api_client,
    custom_detail_action_url,
):
    """Tests the get method :func:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet.download` action
    with the authenticated owner user client.
    """
    response = owner_api_client.get(
        custom_detail_action_url(
            CorrespondentViewSet,
            CorrespondentViewSet.URL_NAME_DOWNLOAD,
            fake_correspondent,
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, FileResponse)
    assert "Content-Disposition" in response.headers
    assert (
        f'filename="{fake_correspondent.name}.vcf"'.replace(" ", "_")
        in response["Content-Disposition"]
    )
    assert "attachment" in response["Content-Disposition"]
    assert "Content-Type" in response.headers
    assert response.headers["Content-Type"] == "text/vcard"
    assert (
        b"".join(response.streaming_content)
        == Correspondent.queryset_as_file(
            Correspondent.objects.filter(id=fake_correspondent.id)
        ).read()
    )


@pytest.mark.django_db
def test_batch_download_noauth(noauth_api_client, custom_list_action_url):
    """Tests the get method :func:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet.download` action
    with an unauthenticated user client.
    """
    response = noauth_api_client.get(
        custom_list_action_url(
            CorrespondentViewSet, CorrespondentViewSet.URL_NAME_DOWNLOAD_BATCH
        ),
        {"id": [1]},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not isinstance(response, FileResponse)


@pytest.mark.django_db
def test_batch_download_auth_other(other_api_client, custom_list_action_url):
    """Tests the get method :func:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet.download` action
    with the authenticated other user client.
    """
    response = other_api_client.get(
        custom_list_action_url(
            CorrespondentViewSet, CorrespondentViewSet.URL_NAME_DOWNLOAD_BATCH
        ),
        {"id": [1, 2]},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert not isinstance(response, FileResponse)


@pytest.mark.django_db
def test_batch_download_no_ids_auth_owner(
    owner_api_client, custom_list_action_url, mock_Correspondent_queryset_as_file
):
    """Tests the get method :func:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet.download` action
    with the authenticated owner user client.
    """
    response = owner_api_client.get(
        custom_list_action_url(
            CorrespondentViewSet, CorrespondentViewSet.URL_NAME_DOWNLOAD_BATCH
        ),
        {},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["id"]
    assert not isinstance(response, FileResponse)
    mock_Correspondent_queryset_as_file.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "bad_ids",
    [
        ["abc"],
        ["1e2"],
        ["5.3"],
        ["4ur"],
    ],
)
def test_batch_download_bad_ids_auth_owner(
    owner_api_client,
    custom_list_action_url,
    mock_Correspondent_queryset_as_file,
    bad_ids,
):
    """Tests the get method :func:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet.download` action
    with the authenticated owner user client.
    """
    response = owner_api_client.get(
        custom_list_action_url(
            CorrespondentViewSet, CorrespondentViewSet.URL_NAME_DOWNLOAD_BATCH
        ),
        {"id": bad_ids},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["id"]
    assert not isinstance(response, FileResponse)
    mock_Correspondent_queryset_as_file.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "ids, expected_ids",
    [
        (["1"], [1]),
        (["1", " 2", "100"], [1, 2, 100]),
        (["1,2", "10"], [1, 2, 10]),
        (["4,6, 8"], [4, 6, 8]),
    ],
)
def test_batch_download_auth_owner(
    fake_file_bytes,
    owner_user,
    owner_api_client,
    custom_list_action_url,
    mock_Correspondent_queryset_as_file,
    ids,
    expected_ids,
):
    """Tests the get method :func:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet.download` action
    with the authenticated owner user client.
    """
    response = owner_api_client.get(
        custom_list_action_url(
            CorrespondentViewSet, CorrespondentViewSet.URL_NAME_DOWNLOAD_BATCH
        ),
        {"id": ids},
    )
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, FileResponse)
    assert "Content-Disposition" in response.headers
    assert 'filename="correspondents.vcf"' in response["Content-Disposition"]
    assert "Content-Type" in response.headers
    assert response.headers["Content-Type"] == "text/vcard"
    assert b"".join(response.streaming_content) == fake_file_bytes
    mock_Correspondent_queryset_as_file.assert_called_once()
    assert list(mock_Correspondent_queryset_as_file.call_args.args[0]) == list(
        Correspondent.objects.filter(pk__in=expected_ids, user=owner_user)
    )


@pytest.mark.django_db
def test_toggle_favorite_noauth(
    fake_correspondent, noauth_api_client, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet.toggle_favorite` action with an unauthenticated user client."""
    response = noauth_api_client.post(
        custom_detail_action_url(
            CorrespondentViewSet,
            CorrespondentViewSet.URL_NAME_TOGGLE_FAVORITE,
            fake_correspondent,
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    fake_correspondent.refresh_from_db()
    assert fake_correspondent.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_other(
    fake_correspondent, other_api_client, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet.toggle_favorite` action with the authenticated other user client."""
    response = other_api_client.post(
        custom_detail_action_url(
            CorrespondentViewSet,
            CorrespondentViewSet.URL_NAME_TOGGLE_FAVORITE,
            fake_correspondent,
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    fake_correspondent.refresh_from_db()
    assert fake_correspondent.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_owner(
    fake_correspondent, owner_api_client, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet.toggle_favorite` action with the authenticated owner user client."""
    response = owner_api_client.post(
        custom_detail_action_url(
            CorrespondentViewSet,
            CorrespondentViewSet.URL_NAME_TOGGLE_FAVORITE,
            fake_correspondent,
        )
    )

    assert response.status_code == status.HTTP_200_OK
    fake_correspondent.refresh_from_db()
    assert fake_correspondent.is_favorite is True
