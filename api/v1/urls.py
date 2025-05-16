# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer
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

Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.views.AccountViewSet import AccountViewSet
from api.v1.views.AttachmentViewSet import AttachmentViewSet
from api.v1.views.CorrespondentViewSet import CorrespondentViewSet
from api.v1.views.DaemonViewSet import DaemonViewSet
from api.v1.views.DatabaseStatsView import DatabaseStatsView
from api.v1.views.EmailViewSet import EmailViewSet
from api.v1.views.MailboxViewSet import MailboxViewSet
from api.v1.views.MailingListViewSet import MailingListViewSet


app_name = "v1"

router = DefaultRouter()
router.register("accounts", AccountViewSet, basename=AccountViewSet.BASENAME)
router.register("mailboxes", MailboxViewSet, basename=MailboxViewSet.BASENAME)
router.register("daemons", DaemonViewSet, basename=DaemonViewSet.BASENAME)
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
router.register(
    "mailinglists",
    MailingListViewSet,
    basename=MailingListViewSet.BASENAME,
)
router.register("emails", EmailViewSet, basename=EmailViewSet.BASENAME)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "stats/",
        DatabaseStatsView.as_view(),
        name=DatabaseStatsView.NAME,
    ),
]
