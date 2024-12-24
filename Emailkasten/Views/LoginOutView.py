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

from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

if TYPE_CHECKING:
    from rest_framework.request import Request


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """View method to log the user in.
        Authenticates the user first and the logs them in with setting the cookie age.

        Args:
            request: The login request.

        Returns:
            A response detailing the login result with CSRF token.
        """
        username = request.data.get('username')
        password = request.data.get('password')
        remember = request.data.get('remember')

        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request=request, username=username, password=password)

        if user is not None:
            login(request, user)

            if remember:
                request.session.set_expiry(settings.SESSION_COOKIE_AGE)
            else:
                request.session.set_expiry(0)

            csrf_token = get_token(request)

            return Response({
                'detail': 'Login successful',
                'csrf_token': csrf_token
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'detail': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)



class LogoutView(APIView):
    def post(self, request: Request) -> Response:
        """View method to log the user out.

        Args:
            request: The logout request.

        Returns:
            A response detailing the logout result.
        """
        logout(request)

        return Response({
            'detail': 'Logout successful'
        }, status=status.HTTP_200_OK)


class CSRFCookieView(APIView):
    permission_classes = [AllowAny]

    @ensure_csrf_cookie
    def get(self, request: Request) -> Response:
        """View method to get a new CSRF token.

        Args:
            request: The get request.

        Returns:
            A response with the CSRF token.
        """
        csrf_token = get_token(request)
        return Response({
            'csrf_token': csrf_token
        })
