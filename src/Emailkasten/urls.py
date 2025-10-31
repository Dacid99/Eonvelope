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

"""URL configuration for Emailkasten project.

The `urlpatterns` list routes URLs to views. For more information please see:

References:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""

from __future__ import annotations

from django.contrib import admin
from django.urls import include, path, re_path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from Emailkasten.views import UserProfileView
from Emailkasten.views.timezone import SET_TIMEZONE_URL_NAME, set_timezone


SCHEMA_NAME = "schema"

urlpatterns = [
    # root
    path("admin/", admin.site.urls),
    path("health/", include("health_check.urls")),
    path("", include("django.conf.urls.i18n")),
    path("settz/", set_timezone, name=SET_TIMEZONE_URL_NAME),
    re_path(r"^robots\.txt", include("robots.urls")),
    # api
    path("api/", include("api.urls")),
    path("api/auth/", include("allauth.headless.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name=SCHEMA_NAME),
    path(
        "api/schema/swagger/",
        SpectacularSwaggerView.as_view(url_name=SCHEMA_NAME),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name=SCHEMA_NAME),
        name="redoc",
    ),
    # web
    path("", include("web.urls")),
    path("users/", include("allauth.urls")),
    path("users/profile/", UserProfileView.as_view(), name=UserProfileView.URL_NAME),
]
