'''
    Emailkasten - a open-source self-hostable email archiving server
    Copyright (C) 2024  David & Philipp Aderbauer

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''
"""
URL configuration for Emailkasten project.

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
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .ViewSets.AccountViewSet import AccountViewSet
from .ViewSets.EMailViewSet import EMailViewSet
from .ViewSets.CorrespondentViewSet import CorrespondentViewSet
from .ViewSets.AttachmentViewSet import AttachmentViewSet
from .ViewSets.ImageViewSet import ImageViewSet
from .ViewSets.MailboxViewSet import MailboxViewSet
from .ViewSets.DatabaseStatsView import DatabaseStatsView
from .ViewSets.UserCreateView import UserViewSet
from .ViewSets.ConfigurationViewSet import ConfigurationViewSet
from .ViewSets.LoginOut import LoginView, LogoutView, CSRFCookieView

router = DefaultRouter()
router.register(r'accounts', AccountViewSet)
router.register(r'mailboxes', MailboxViewSet)
router.register(r'emails', EMailViewSet)
router.register(r'correspondents', CorrespondentViewSet)
router.register(r'attachments', AttachmentViewSet)
router.register(r'images', ImageViewSet)
router.register(r'config', ConfigurationViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path('login/', LoginView.as_view(), name = 'login'),
    path('logout/', LogoutView.as_view(), name = 'logout'),
    path('csrf-token/', CSRFCookieView.as_view(), name = 'csrf-token'),
    path("api/schema/", SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path("health/", include('health_check.urls')),
    path('stats/', DatabaseStatsView.as_view(), name = 'stats'),
    path('', include(router.urls)),
    path("api-auth/", include('rest_framework.urls', namespace='rest_framework')), 
]
