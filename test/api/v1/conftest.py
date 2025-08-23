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

"""File with fixtures required for all viewset tests. Automatically imported to `test_` files.

The serializer tests are made against a mocked consistent database with an instance of every model in every testcase.
"""

from __future__ import annotations

import pytest
from django.forms.models import model_to_dict
from django_celery_beat.models import IntervalSchedule
from model_bakery import baker


@pytest.fixture
def daemon_with_interval_payload(daemon_payload):
    """Payload for a daemon form."""
    interval = baker.prepare(IntervalSchedule)
    daemon_payload["interval"] = model_to_dict(interval)
    daemon_payload["interval"]["every"] = abs(daemon_payload["interval"]["every"])
    return daemon_payload
