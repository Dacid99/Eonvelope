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

from .Views.AccountViewSet import AccountViewSet
from .Views.AttachmentViewSet import AttachmentViewSet
from .Views.ConfigurationViewSet import ConfigurationViewSet
from .Views.CorrespondentViewSet import CorrespondentViewSet
from .Views.DaemonViewSet import DaemonViewSet
from .Views.DatabaseStatsView import DatabaseStatsView
from .Views.EMailViewSet import EMailViewSet
from .Views.ImageViewSet import ImageViewSet
from .Views.LoginOutView import CSRFCookieView, LoginView, LogoutView
from .Views.MailboxViewSet import MailboxViewSet
from .Views.UserCreateView import UserViewSet

router = DefaultRouter()
router.register(r'accounts', AccountViewSet)
router.register(r'mailboxes', MailboxViewSet)
router.register(r'daemons', DaemonViewSet)
router.register(r'emails', EMailViewSet)
router.register(r'correspondents', CorrespondentViewSet)
router.register(r'attachments', AttachmentViewSet)
router.register(r'images', ImageViewSet)
router.register(r'config', ConfigurationViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', DatabaseStatsView.as_view(), name = 'stats'),
    path('login/', LoginView.as_view(), name = 'login'),
    path('logout/', LogoutView.as_view(), name = 'logout'),
    path('csrf-token/', CSRFCookieView.as_view(), name = 'csrf-token'),
]
