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

"""File with fixtures required for all viewset tests. Automatically imported to `test_` files.

The serializer tests are made against a mocked consistent database with an instance of every model in every testcase.
"""

from __future__ import annotations

import pytest
from django.forms.models import model_to_dict
from django.urls import reverse
from django_celery_beat.models import IntervalSchedule
from model_bakery import baker


@pytest.fixture
def daemon_with_interval_payload(daemon_payload):
    """Payload for a daemon form."""
    interval = baker.prepare(IntervalSchedule)
    daemon_payload["interval"] = model_to_dict(interval)
    daemon_payload["interval"]["every"] = abs(daemon_payload["interval"]["every"])
    return daemon_payload


@pytest.fixture(scope="package")
def list_url():
    """Callable getting the viewsets url for list actions."""
    return lambda viewset_class: reverse(f"api:v1:{viewset_class.BASENAME}-list")


@pytest.fixture(scope="package")
def detail_url():
    """Callable getting the viewsets url for detail actions."""
    return lambda viewset_class, instance: reverse(
        f"api:v1:{viewset_class.BASENAME}-detail", args=[instance.id]
    )


@pytest.fixture(scope="package")
def custom_list_action_url():
    """Callable getting the viewsets url for custom list actions."""
    return lambda viewset_class, custom_list_action_url_name: (
        reverse(f"api:v1:{viewset_class.BASENAME}-{custom_list_action_url_name}")
    )


@pytest.fixture(scope="package")
def custom_detail_action_url():
    """Callable getting the viewsets url for custom detail actions."""
    return lambda viewset_class, custom_detail_action_url_name, instance: (
        reverse(
            f"api:v1:{viewset_class.BASENAME}-{custom_detail_action_url_name}",
            args=[instance.id],
        )
    )
