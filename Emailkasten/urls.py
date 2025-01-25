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
"""
URL configuration for Emailkasten app.

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
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views.AccountViewSet import AccountViewSet
from api.views.AttachmentViewSet import AttachmentViewSet
from api.views.ConfigurationViewSet import ConfigurationViewSet
from api.views.CorrespondentViewSet import CorrespondentViewSet
from api.views.DaemonViewSet import DaemonViewSet
from api.views.DatabaseStatsView import DatabaseStatsView
from api.views.EMailViewSet import EMailViewSet
from api.views.ImageViewSet import ImageViewSet
from api.views.MailboxViewSet import MailboxViewSet
from api.views.MailingListViewSet import MailingListViewSet
from api.views.UserViewSet import UserViewSet

router = DefaultRouter()
router.register(rf'{AccountViewSet.BASENAME}', AccountViewSet, basename=AccountViewSet.BASENAME)
router.register(rf'{MailboxViewSet.BASENAME}', MailboxViewSet, basename=MailboxViewSet.BASENAME)
router.register(rf'{DaemonViewSet.BASENAME}', DaemonViewSet, basename=DaemonViewSet.BASENAME)
router.register(rf'{EMailViewSet.BASENAME}', EMailViewSet, basename=EMailViewSet.BASENAME)
router.register(rf'{CorrespondentViewSet.BASENAME}', CorrespondentViewSet, basename=CorrespondentViewSet.BASENAME)
router.register(rf'{AttachmentViewSet.BASENAME}', AttachmentViewSet, basename=AttachmentViewSet.BASENAME)
router.register(rf'{ImageViewSet.BASENAME}', ImageViewSet, basename=ImageViewSet.BASENAME)
router.register(rf'{ConfigurationViewSet.BASENAME}', ConfigurationViewSet, basename=ConfigurationViewSet.BASENAME)
router.register(rf'{UserViewSet.BASENAME}', UserViewSet, basename=UserViewSet.BASENAME)
router.register(rf'{MailingListViewSet.BASENAME}', MailingListViewSet, basename=MailingListViewSet.BASENAME)

urlpatterns = [
    path('', include(router.urls)),
    path(f'{DatabaseStatsView.NAME}/', DatabaseStatsView.as_view(), name = DatabaseStatsView.NAME),
]
