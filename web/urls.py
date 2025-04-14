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

from django.urls import path
from django.views.generic import RedirectView

from .views.account_views import (
    AccountCreateView,
    AccountDetailWithDeleteView,
    AccountFilterView,
    AccountUpdateOrDeleteView,
)
from .views.attachment_views import AttachmentDetailWithDeleteView, AttachmentFilterView
from .views.correspondent_views import (
    CorrespondentDetailWithDeleteView,
    CorrespondentFilterView,
    CorrespondentUpdateOrDeleteView,
)
from .views.daemon_views import (
    DaemonDetailWithDeleteView,
    DaemonFilterView,
    DaemonUpdateOrDeleteView,
)
from .views.DashboardView import DashboardView
from .views.email_views import EMailDetailWithDeleteView, EMailFilterView
from .views.mailbox_views import (
    MailboxDetailWithDeleteView,
    MailboxFilterView,
    MailboxUpdateOrDeleteView,
)
from .views.mailinglist_views import (
    MailingListDetailWithDeleteView,
    MailingListFilterView,
)


app_name = "web"

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name=DashboardView.URL_NAME),
    path("", RedirectView.as_view(url="dashboard/", permanent=True)),
    path(
        "accounts/",
        AccountFilterView.AccountFilterView.as_view(),
        name=AccountFilterView.AccountFilterView.URL_NAME,
    ),
    path(
        "accounts/<int:pk>/details/",
        AccountDetailWithDeleteView.AccountDetailWithDeleteView.as_view(),
        name=AccountDetailWithDeleteView.AccountDetailWithDeleteView.URL_NAME,
    ),
    path(
        "accounts/<int:pk>/edit/",
        AccountUpdateOrDeleteView.AccountUpdateOrDeleteView.as_view(),
        name=AccountUpdateOrDeleteView.AccountUpdateOrDeleteView.URL_NAME,
    ),
    path(
        "accounts/add/",
        AccountCreateView.AccountCreateView.as_view(),
        name=AccountCreateView.AccountCreateView.URL_NAME,
    ),
    path(
        "attachments/",
        AttachmentFilterView.AttachmentFilterView.as_view(),
        name=AttachmentFilterView.AttachmentFilterView.URL_NAME,
    ),
    path(
        "attachments/<int:pk>/details/",
        AttachmentDetailWithDeleteView.AttachmentDetailWithDeleteView.as_view(),
        name=AttachmentDetailWithDeleteView.AttachmentDetailWithDeleteView.URL_NAME,
    ),
    path(
        "correspondents/",
        CorrespondentFilterView.CorrespondentFilterView.as_view(),
        name=CorrespondentFilterView.CorrespondentFilterView.URL_NAME,
    ),
    path(
        "correspondents/<int:pk>/details/",
        CorrespondentDetailWithDeleteView.CorrespondentDetailWithDeleteView.as_view(),
        name=CorrespondentDetailWithDeleteView.CorrespondentDetailWithDeleteView.URL_NAME,
    ),
    path(
        "correspondents/<int:pk>/edit/",
        CorrespondentUpdateOrDeleteView.CorrespondentUpdateOrDeleteView.as_view(),
        name=CorrespondentUpdateOrDeleteView.CorrespondentUpdateOrDeleteView.URL_NAME,
    ),
    path(
        "daemons/",
        DaemonFilterView.DaemonFilterView.as_view(),
        name=DaemonFilterView.DaemonFilterView.URL_NAME,
    ),
    path(
        "daemons/<int:pk>/details/",
        DaemonDetailWithDeleteView.DaemonDetailWithDeleteView.as_view(),
        name=DaemonDetailWithDeleteView.DaemonDetailWithDeleteView.URL_NAME,
    ),
    path(
        "daemons/<int:pk>/edit/",
        DaemonUpdateOrDeleteView.DaemonUpdateOrDeleteView.as_view(),
        name=DaemonUpdateOrDeleteView.DaemonUpdateOrDeleteView.URL_NAME,
    ),
    path(
        "emails/",
        EMailFilterView.EMailFilterView.as_view(),
        name=EMailFilterView.EMailFilterView.URL_NAME,
    ),
    path(
        "emails/<int:pk>/details/",
        EMailDetailWithDeleteView.EMailDetailWithDeleteView.as_view(),
        name=EMailDetailWithDeleteView.EMailDetailWithDeleteView.URL_NAME,
    ),
    path(
        "mailboxes/",
        MailboxFilterView.MailboxFilterView.as_view(),
        name=MailboxFilterView.MailboxFilterView.URL_NAME,
    ),
    path(
        "mailboxes/<int:pk>/details/",
        MailboxDetailWithDeleteView.MailboxDetailWithDeleteView.as_view(),
        name=MailboxDetailWithDeleteView.MailboxDetailWithDeleteView.URL_NAME,
    ),
    path(
        "mailboxes/<int:pk>/edit/",
        MailboxUpdateOrDeleteView.MailboxUpdateOrDeleteView.as_view(),
        name=MailboxUpdateOrDeleteView.MailboxUpdateOrDeleteView.URL_NAME,
    ),
    path(
        "mailinglists/",
        MailingListFilterView.MailingListFilterView.as_view(),
        name=MailingListFilterView.MailingListFilterView.URL_NAME,
    ),
    path(
        "mailinglists/<int:pk>/details/",
        MailingListDetailWithDeleteView.MailingListDetailWithDeleteView.as_view(),
        name=MailingListDetailWithDeleteView.MailingListDetailWithDeleteView.URL_NAME,
    ),
]
