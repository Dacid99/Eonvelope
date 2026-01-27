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
"""URL configuration for api app version 1.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/

References:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.views import (
    AccountViewSet,
    AttachmentViewSet,
    CorrespondentViewSet,
    DaemonViewSet,
    DatabaseStatsView,
    EmailViewSet,
    MailboxViewSet,
    UserProfileView,
)

app_name = "v1"

router = DefaultRouter(
    trailing_slash=False
)  # no slash for data endpoints for consistency with allauth headless api
router.register("accounts", AccountViewSet, basename=AccountViewSet.BASENAME)
router.register("mailboxes", MailboxViewSet, basename=MailboxViewSet.BASENAME)
router.register("routines", DaemonViewSet, basename=DaemonViewSet.BASENAME)
router.register(
    "correspondents",
    CorrespondentViewSet,
    basename=CorrespondentViewSet.BASENAME,
)
router.register(
    "attachments",
    AttachmentViewSet,
    basename=AttachmentViewSet.BASENAME,
)
router.register("emails", EmailViewSet, basename=EmailViewSet.BASENAME)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "stats",
        DatabaseStatsView.as_view(),
        name=DatabaseStatsView.NAME,
    ),
    path(
        "auth/profile",
        UserProfileView.as_view(),
        name=UserProfileView.NAME,
    ),
]
