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
"""URL configuration for api app.

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

from .views.account_views import AccountDetailView, AccountFilterView
from .views.attachment_views import AttachmentDetailView, AttachmentFilterView
from .views.correspondent_views import CorrespondentDetailView, CorrespondentFilterView
from .views.daemon_views import DaemonDetailView, DaemonFilterView
from .views.email_views import EMailDetailView, EMailFilterView
from .views.mailbox_views import MailboxDetailView, MailboxFilterView
from .views.mailinglist_views import MailingListDetailView, MailingListFilterView


app_name = "web"

urlpatterns = [
    path("users/", include("allauth.urls")),
    path(
        "accounts/",
        AccountFilterView.AccountFilterView.as_view(),
        name=AccountFilterView.AccountFilterView.URL_NAME,
    ),
    path(
        "account/<int:pk>/",
        AccountDetailView.AccountDetailView.as_view(),
        name=AccountDetailView.AccountDetailView.URL_NAME,
    ),
    path(
        "attachments/",
        AttachmentFilterView.AttachmentFilterView.as_view(),
        name=AttachmentFilterView.AttachmentFilterView.URL_NAME,
    ),
    path(
        "attachment/<int:pk>/",
        AttachmentDetailView.AttachmentDetailView.as_view(),
        name=AttachmentDetailView.AttachmentDetailView.URL_NAME,
    ),
    path(
        "correspondents/",
        CorrespondentFilterView.CorrespondentFilterView.as_view(),
        name=CorrespondentFilterView.CorrespondentFilterView.URL_NAME,
    ),
    path(
        "correspondent/<int:pk>/",
        CorrespondentDetailView.CorrespondentDetailView.as_view(),
        name=CorrespondentDetailView.CorrespondentDetailView.URL_NAME,
    ),
    path(
        "daemons/",
        DaemonFilterView.DaemonFilterView.as_view(),
        name=DaemonFilterView.DaemonFilterView.URL_NAME,
    ),
    path(
        "daemon/<int:pk>/",
        DaemonDetailView.DaemonDetailView.as_view(),
        name=DaemonDetailView.DaemonDetailView.URL_NAME,
    ),
    path(
        "emails/",
        EMailFilterView.EMailFilterView.as_view(),
        name=EMailFilterView.EMailFilterView.URL_NAME,
    ),
    path(
        "email/<int:pk>/",
        EMailDetailView.EMailDetailView.as_view(),
        name=EMailDetailView.EMailDetailView.URL_NAME,
    ),
    path(
        "mailboxes/",
        MailboxFilterView.MailboxFilterView.as_view(),
        name=MailboxFilterView.MailboxFilterView.URL_NAME,
    ),
    path(
        "mailbox/<int:pk>/",
        MailboxDetailView.MailboxDetailView.as_view(),
        name=MailboxDetailView.MailboxDetailView.URL_NAME,
    ),
    path(
        "mailinglists/",
        MailingListFilterView.MailingListFilterView.as_view(),
        name=MailingListFilterView.MailingListFilterView.URL_NAME,
    ),
    path(
        "mailinglist/<int:pk>/",
        MailingListDetailView.MailingListDetailView.as_view(),
        name=MailingListDetailView.MailingListDetailView.URL_NAME,
    ),
]
