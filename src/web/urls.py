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
"""URL configuration for web app.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/

References:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""

from __future__ import annotations

from django.urls import path
from django.views.generic import RedirectView

from .views import (
    AccountCreateView,
    AccountDetailWithDeleteView,
    AccountEmailsFilterView,
    AccountEmailsTableView,
    AccountFilterView,
    AccountTableView,
    AccountUpdateOrDeleteView,
    AttachmentDetailWithDeleteView,
    AttachmentFilterView,
    AttachmentTableView,
    CorrespondentDetailWithDeleteView,
    CorrespondentEmailsFilterView,
    CorrespondentEmailsTableView,
    CorrespondentFilterView,
    CorrespondentTableView,
    CorrespondentUpdateOrDeleteView,
    DaemonCreateView,
    DaemonDetailWithDeleteView,
    DaemonFilterView,
    DaemonTableView,
    DaemonUpdateOrDeleteView,
    DashboardView,
    EmailArchiveIndexView,
    EmailConversationTableView,
    EmailConversationView,
    EmailDayArchiveView,
    EmailDetailWithDeleteView,
    EmailFilterView,
    EmailMonthArchiveView,
    EmailTableView,
    EmailWeekArchiveView,
    EmailYearArchiveView,
    MailboxCreateDaemonView,
    MailboxDetailWithDeleteView,
    MailboxEmailsFilterView,
    MailboxEmailsTableView,
    MailboxFilterView,
    MailboxTableView,
    MailboxUpdateOrDeleteView,
    UploadEmailView,
)


app_name = "web"

# be cautious when changing the view url names, template optics may depend on them!

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name=DashboardView.URL_NAME),
    path(
        "",
        RedirectView.as_view(
            pattern_name=app_name + ":" + DashboardView.URL_NAME, permanent=True
        ),
    ),
    path(
        "accounts/",
        AccountFilterView.as_view(),
        name=AccountFilterView.URL_NAME,
    ),
    path(
        "accounts/table/",
        AccountTableView.as_view(),
        name=AccountTableView.URL_NAME,
    ),
    path(
        "accounts/<int:pk>/",
        AccountDetailWithDeleteView.as_view(),
        name=AccountDetailWithDeleteView.URL_NAME,
    ),
    path(
        "accounts/<int:pk>/emails/",
        AccountEmailsFilterView.as_view(),
        name=AccountEmailsFilterView.URL_NAME,
    ),
    path(
        "accounts/<int:pk>/emails/table/",
        AccountEmailsTableView.as_view(),
        name=AccountEmailsTableView.URL_NAME,
    ),
    path(
        "accounts/<int:pk>/edit/",
        AccountUpdateOrDeleteView.as_view(),
        name=AccountUpdateOrDeleteView.URL_NAME,
    ),
    path(
        "accounts/add/",
        AccountCreateView.as_view(),
        name=AccountCreateView.URL_NAME,
    ),
    path(
        "attachments/",
        AttachmentFilterView.as_view(),
        name=AttachmentFilterView.URL_NAME,
    ),
    path(
        "attachments/table/",
        AttachmentTableView.as_view(),
        name=AttachmentTableView.URL_NAME,
    ),
    path(
        "attachments/<int:pk>/",
        AttachmentDetailWithDeleteView.as_view(),
        name=AttachmentDetailWithDeleteView.URL_NAME,
    ),
    path(
        "correspondents/",
        CorrespondentFilterView.as_view(),
        name=CorrespondentFilterView.URL_NAME,
    ),
    path(
        "correspondents/table/",
        CorrespondentTableView.as_view(),
        name=CorrespondentTableView.URL_NAME,
    ),
    path(
        "correspondents/<int:pk>/",
        CorrespondentDetailWithDeleteView.as_view(),
        name=CorrespondentDetailWithDeleteView.URL_NAME,
    ),
    path(
        "correspondents/<int:pk>/emails/",
        CorrespondentEmailsFilterView.as_view(),
        name=CorrespondentEmailsFilterView.URL_NAME,
    ),
    path(
        "correspondents/<int:pk>/emails/table/",
        CorrespondentEmailsTableView.as_view(),
        name=CorrespondentEmailsTableView.URL_NAME,
    ),
    path(
        "correspondents/<int:pk>/edit/",
        CorrespondentUpdateOrDeleteView.as_view(),
        name=CorrespondentUpdateOrDeleteView.URL_NAME,
    ),
    path(
        "routines/",
        DaemonFilterView.as_view(),
        name=DaemonFilterView.URL_NAME,
    ),
    path(
        "routines/table/",
        DaemonTableView.as_view(),
        name=DaemonTableView.URL_NAME,
    ),
    path(
        "routines/<int:pk>/",
        DaemonDetailWithDeleteView.as_view(),
        name=DaemonDetailWithDeleteView.URL_NAME,
    ),
    path(
        "routines/<int:pk>/edit/",
        DaemonUpdateOrDeleteView.as_view(),
        name=DaemonUpdateOrDeleteView.URL_NAME,
    ),
    path(
        "routines/add/",
        DaemonCreateView.as_view(),
        name=DaemonCreateView.URL_NAME,
    ),
    path(
        "emails/",
        EmailFilterView.as_view(),
        name=EmailFilterView.URL_NAME,
    ),
    path(
        "emails/table/",
        EmailTableView.as_view(),
        name=EmailTableView.URL_NAME,
    ),
    path(
        "emails/<int:pk>/",
        EmailDetailWithDeleteView.as_view(),
        name=EmailDetailWithDeleteView.URL_NAME,
    ),
    path(
        "emails/<int:pk>/conversation/",
        EmailConversationView.as_view(),
        name=EmailConversationView.URL_NAME,
    ),
    path(
        "emails/<int:pk>/conversation/table/",
        EmailConversationTableView.as_view(),
        name=EmailConversationTableView.URL_NAME,
    ),
    path(
        "emails/archive/",
        EmailArchiveIndexView.as_view(),
        name=EmailArchiveIndexView.URL_NAME,
    ),
    path(
        "emails/archive/<int:year>",
        EmailYearArchiveView.as_view(),
        name=EmailYearArchiveView.URL_NAME,
    ),
    path(
        "emails/archive/<int:year>/<int:month>",
        EmailMonthArchiveView.as_view(),
        name=EmailMonthArchiveView.URL_NAME,
    ),
    path(
        "emails/archive/<int:year>/week/<int:week>",
        EmailWeekArchiveView.as_view(),
        name=EmailWeekArchiveView.URL_NAME,
    ),
    path(
        "emails/archive/<int:year>/<int:month>/<int:day>",
        EmailDayArchiveView.as_view(),
        name=EmailDayArchiveView.URL_NAME,
    ),
    path(
        "mailboxes/",
        MailboxFilterView.as_view(),
        name=MailboxFilterView.URL_NAME,
    ),
    path(
        "mailboxes/table/",
        MailboxTableView.as_view(),
        name=MailboxTableView.URL_NAME,
    ),
    path(
        "mailboxes/<int:pk>/",
        MailboxDetailWithDeleteView.as_view(),
        name=MailboxDetailWithDeleteView.URL_NAME,
    ),
    path(
        "mailboxes/<int:pk>/emails/",
        MailboxEmailsFilterView.as_view(),
        name=MailboxEmailsFilterView.URL_NAME,
    ),
    path(
        "mailboxes/<int:pk>/emails/table/",
        MailboxEmailsTableView.as_view(),
        name=MailboxEmailsTableView.URL_NAME,
    ),
    path(
        "mailboxes/<int:pk>/edit/",
        MailboxUpdateOrDeleteView.as_view(),
        name=MailboxUpdateOrDeleteView.URL_NAME,
    ),
    path(
        "mailboxes/<int:pk>/add-routine/",
        MailboxCreateDaemonView.as_view(),
        name=MailboxCreateDaemonView.URL_NAME,
    ),
    path(
        "mailboxes/<int:pk>/upload/",
        UploadEmailView.as_view(),
        name=UploadEmailView.URL_NAME,
    ),
]
