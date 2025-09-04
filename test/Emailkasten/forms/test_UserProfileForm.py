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

"""Test module for the :class:`Emailkasten.forms.UserProfileForm` form class."""

import pytest

from Emailkasten.forms import UserProfileForm


@pytest.mark.django_db
def test_post(owner_user, profile_payload):
    """Tests post direction of :class:`web.forms.UserProfileForm`."""
    form = UserProfileForm(instance=owner_user.profile, data=profile_payload)

    assert form.is_valid()
    form_data = form.cleaned_data
    assert "paperless_url" in form_data
    assert form_data["paperless_url"] == profile_payload["paperless_url"]
    assert "paperless_api_key" in form_data
    assert form_data["paperless_api_key"] == profile_payload["paperless_api_key"]
    assert "paperless_tika_enabled" in form_data
    assert (
        form_data["paperless_tika_enabled"] == profile_payload["paperless_tika_enabled"]
    )
    assert "user" not in form_data
    assert len(form_data) == 3


@pytest.mark.django_db
@pytest.mark.parametrize("bad_protocol", ["ftp://", "ftps://", "other://"])
def test_post_bad_paperless_url_protocol(
    faker, owner_user, profile_payload, bad_protocol
):
    """Tests post direction of :class:`web.forms.UserProfileForm`."""
    profile_payload["paperless_url"] = bad_protocol + faker.ipv4()

    form = UserProfileForm(instance=owner_user.profile, data=profile_payload)

    assert not form.is_valid()
    assert form["paperless_url"].errors


@pytest.mark.django_db
def test_get(owner_user):
    """Tests get direction of :class:`web.forms.UserProfileForm`."""
    form = UserProfileForm(instance=owner_user.profile)
    form_initial_data = form.initial
    form_fields = form.fields

    assert "paperless_url" in form_fields
    assert "paperless_url" in form_initial_data
    assert form_initial_data["paperless_url"] == owner_user.profile.paperless_url
    assert "paperless_api_key" in form_fields
    assert "paperless_api_key" in form_initial_data
    assert (
        form_initial_data["paperless_api_key"] == owner_user.profile.paperless_api_key
    )
    assert "paperless_tika_enabled" in form_fields
    assert "paperless_tika_enabled" in form_initial_data
    assert (
        form_initial_data["paperless_tika_enabled"]
        == owner_user.profile.paperless_tika_enabled
    )
    assert "user" not in form_fields
    assert len(form_fields) == 3
