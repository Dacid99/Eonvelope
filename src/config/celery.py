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

"""Celery module for Eonvelope project."""

import os
import sys
from pathlib import Path

from celery import Celery

sys.path.append(str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("eonvelope")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
