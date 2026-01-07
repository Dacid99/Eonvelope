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

"""Main URL configuration for Eonvelope project.

The `urlpatterns` list routes URLs to views. For more information please see:

References:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""
from __future__ import annotations

from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


SCHEMA_NAME = "schema"

urlpatterns = [
    # root
    path("admin/", admin.site.urls),
    path("", include("django.conf.urls.i18n")),
    path("", include("pwa.urls")),
    path("health/", include("health_check.urls")),
    path("users/", include("allauth.urls")),
    # api
    path("api/", include("api.urls")),
    path("api/auth/", include("allauth.headless.urls")),
    # web
    path("", include("web.urls")),
    # eonvelope
    path("", include("eonvelope.urls")),
    *debug_toolbar_urls(),
]
if not settings.SLIM:
    urlpatterns += [
        path("robots.txt", include("robots.urls")),
        path("db-schema/", include("schema_viewer.urls")),
        path("", include("django_prometheus.urls")),
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
    ]
