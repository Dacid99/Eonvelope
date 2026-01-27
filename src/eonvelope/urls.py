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

"""URL configuration for Eonvelope project.

The `urlpatterns` list routes URLs to views. For more information please see:

References:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""

from __future__ import annotations

from django.urls import path

from eonvelope.views import UserProfileView
from eonvelope.views.timezone import SET_TIMEZONE_URL_NAME, set_timezone

urlpatterns = [
    path("settz/", set_timezone, name=SET_TIMEZONE_URL_NAME),
    path("users/profile/", UserProfileView.as_view(), name=UserProfileView.URL_NAME),
]
