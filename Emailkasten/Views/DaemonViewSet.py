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

"""Module with the :class:`DaemonViewSet` viewset."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from django.http import FileResponse, Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..EMailArchiverDaemon import EMailArchiverDaemon
from ..Filters.DaemonFilter import DaemonFilter
from ..Models.DaemonModel import DaemonModel
from ..Serializers.DaemonSerializers.DaemonSerializer import \
    DaemonSerializer

if TYPE_CHECKING:
    from rest_framework.request import Request
    from django.db.models import BaseManager


class DaemonViewSet(viewsets.ModelViewSet):
    """Viewset for the :class:`Emailkasten.Models.DaemonModel.DaemonModel`."""

    queryset = DaemonModel.objects.all()
    serializer_class = DaemonSerializer
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_class = DaemonFilter
    permission_classes = [IsAuthenticated]
    ordering_fields = ['fetching_criterion', 'is_running', 'is_healthy', 'mailbox__fetching_criterion', 'mailbox__name', 'mailbox__account__mail_address', 'mailbox__account__mail_host', 'mailbox__account__protocol', 'created', 'updated']
    ordering = ['id']


    def get_queryset(self) -> BaseManager[DaemonModel]:
        """Filters the data for entries connected to the request user.

        Returns:
            The daemon entries matching the request user."""
        return DaemonModel.objects.filter(mailbox__account__user = self.request.user)


    @action(detail=True, methods=['get'])
    def fetching_options(self, request: Request, pk: int|None = None) -> Response:
        """Action method returning all fetching options for the daemon.

        Args:
            request: The request triggering the action.
            pk: int: The private key of the daemon. Defaults to None.

        Returns:
            A response detailing the request status.
        """
        daemon = self.get_object()

        availableFetchingOptions = daemon.mailbox.getAvailableFetchingCriteria()
        if availableFetchingOptions:
            return Response({'options': availableFetchingOptions})
        else:
            return Response({'error': "No fetching options available for this mailbox!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @action(detail=True, methods=['post'], url_path='test')
    def test(self, request: Request, pk:int|None = None) -> Response:
        """Action method testing the daemon data of the mailbox.

        Args:
            request: The request triggering the action.
            pk: The private key of the daemon. Defaults to None.

        Returns:
            A response detailing the test result for the daemon.
        """
        daemon = self.get_object()
        return EMailArchiverDaemon.testDaemon(daemon)


    @action(detail=True, methods=['post'], url_path='start')
    def start(self, request: Request, pk: int|None = None) -> Response:
        """Action method starting the daemon for the mailbox.

        Args:
            request: The request triggering the action.
            pk: The private key of the daemon. Defaults to None.

        Returns:
            A response detailing the start result of the daemon.
        """
        daemon = self.get_object()
        return EMailArchiverDaemon.startDaemon(daemon)


    @action(detail=True, methods=['post'], url_path='stop')
    def stop(self, request: Request, pk: int|None = None) -> Response:
        """Action method stopping the daemon data of the mailbox.

        Args:
            request: The request triggering the action.
            pk: The private key of the daemon. Defaults to None.

        Returns:
            A response detailing the stop result for the daemon.
        """
        daemon = self.get_object()
        return EMailArchiverDaemon.stopDaemon(daemon)


    @action(detail=True, methods=['get'], url_path='log/download')
    def log_download(self, request: Request, pk: int|None = None) -> FileResponse:
        """Action method downloading the log file of the daemon.

        Args:
            request: The request triggering the action.
            pk: int: The private key of the daemon. Defaults to None.

        Raises:
            Http404: If the filepath is not in the database or it doesnt exist.

        Returns:
            A fileresponse containing the requested file.
        """
        daemon = self.get_object()

        daemonLogFilepath = daemon.log_filepath
        if not daemonLogFilepath or not os.path.exists(daemonLogFilepath):
            raise Http404("Log file not found")

        daemonLogFilename = os.path.basename(daemonLogFilepath)
        with open(daemonLogFilepath, 'rb') as daemonLogFile:
            response = FileResponse(daemonLogFile, as_attachment=True, filename=daemonLogFilename)
            return response
