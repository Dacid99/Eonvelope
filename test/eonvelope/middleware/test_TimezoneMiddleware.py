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

"""Test module for the :class:`TimezoneMiddleware`."""

import pytest
from django.conf import settings
from django.utils import timezone

from eonvelope.middleware.TimezoneMiddleware import TimezoneMiddleware


@pytest.mark.django_db
def test_good_timezone(fake_timezone, client):
    """Tests setting of the session timezone by :class:`eonvelope.middleware.TimezoneMiddleware`
    in case a valid timezone is in the session.
    """
    session = client.session
    session[TimezoneMiddleware.TIMEZONE_SESSION_KEY] = fake_timezone
    session.save()

    assert timezone.get_current_timezone_name() == settings.TIME_ZONE

    client.get("/")

    assert timezone.get_current_timezone_name() == fake_timezone

    timezone.deactivate()


@pytest.mark.django_db
def test__bad_timezone(client):
    """Tests setting of the session timezone by :class:`eonvelope.middleware.TimezoneMiddleware`
    in case an invalid timezone is in the session.
    """
    session = client.session
    session[TimezoneMiddleware.TIMEZONE_SESSION_KEY] = "NO/TZONE"
    session.save()

    assert timezone.get_current_timezone_name() == settings.TIME_ZONE

    client.get("/")

    assert timezone.get_current_timezone_name() == settings.TIME_ZONE

    timezone.deactivate()


@pytest.mark.django_db
def test__no_timezone(client):
    """Tests setting of the session timezone by :class:`eonvelope.middleware.TimezoneMiddleware`
    in case no timezone is in the session.
    """
    assert timezone.get_current_timezone_name() == settings.TIME_ZONE

    client.get("/")

    assert timezone.get_current_timezone_name() == settings.TIME_ZONE

    timezone.deactivate()
