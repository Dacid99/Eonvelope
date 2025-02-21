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
from typing import TYPE_CHECKING, Any, Final

from django.http import FileResponse, Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from typing_extensions import override

from core.EMailArchiverDaemonRegistry import EMailArchiverDaemonRegistry
from core.models.DaemonModel import DaemonModel

from ..filters.DaemonFilter import DaemonFilter
from ..serializers.daemon_serializers.BaseDaemonSerializer import BaseDaemonSerializer


if TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework.permissions import BasePermission
    from rest_framework.request import Request


class DaemonViewSet(viewsets.ModelViewSet):
    """Viewset for the :class:`core.models.DaemonModel.DaemonModel`."""

    BASENAME = "daemons"
    serializer_class = BaseDaemonSerializer
    filter_backends: Final[list] = [DjangoFilterBackend, OrderingFilter]
    filterset_class = DaemonFilter
    permission_classes: Final[list[type[BasePermission]]] = [IsAuthenticated]
    ordering_fields: Final[list[str]] = [
        "fetching_criterion",
        "cycle_interval",
        "restart_time",
        "is_running",
        "is_healthy",
        "mailbox__fetching_criterion",
        "mailbox__name",
        "mailbox__account__mail_address",
        "mailbox__account__mail_host",
        "mailbox__account__protocol",
        "created",
        "updated",
    ]
    ordering: Final[list[str]] = ["id"]

    @override
    def get_queryset(self) -> QuerySet[DaemonModel]:
        """Filters the data for entries connected to the request user.

        Returns:
            The daemon entries matching the request user.
        """
        return DaemonModel.objects.filter(mailbox__account__user=self.request.user)

    @override
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Disables the POST method for this viewset."""
        return Response(
            {"detail": "POST method is not allowed on this endpoint."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    URL_PATH_FETCHING_OPTIONS = "fetching-options"
    URL_NAME_FETCHING_OPTIONS = "fetching-options"

    @action(
        detail=True,
        methods=["get"],
        url_path=URL_PATH_FETCHING_OPTIONS,
        url_name=URL_NAME_FETCHING_OPTIONS,
    )
    def fetching_options(self, request: Request, pk: int | None = None) -> Response:
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
            return Response({"options": availableFetchingOptions})
        return Response(
            {"error": "No fetching options available for this mailbox!"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    URL_PATH_TEST = "test"
    URL_NAME_TEST = "test"

    @action(
        detail=True, methods=["post"], url_path=URL_PATH_TEST, url_name=URL_NAME_TEST
    )
    def test(self, request: Request, pk: int | None = None) -> Response:
        """Action method testing the daemon data of the mailbox.

        Args:
            request: The request triggering the action.
            pk: The private key of the daemon. Defaults to None.

        Returns:
            A response detailing the test result for the daemon.
        """
        daemon = self.get_object()
        daemonData = self.get_serializer(daemon).data
        result = EMailArchiverDaemonRegistry.testDaemon(daemon)

        return Response(
            {
                "detail": (
                    "Daemon testrun was successful."
                    if result
                    else "Daemon testrun failed!"
                ),
                "daemon": daemonData,
                "result": result,
            }
        )

    URL_PATH_START = "start"
    URL_NAME_START = "start"

    @action(
        detail=True, methods=["post"], url_path=URL_PATH_START, url_name=URL_NAME_START
    )
    def start(self, request: Request, pk: int | None = None) -> Response:
        """Action method starting the daemon for the mailbox.

        Args:
            request: The request triggering the action.
            pk: The private key of the daemon. Defaults to None.

        Returns:
            A response detailing the start result of the daemon.
        """
        daemon = self.get_object()
        daemonData = self.get_serializer(daemon).data
        result = EMailArchiverDaemonRegistry.startDaemon(daemon)
        if result:
            return Response({"detail": "Daemon started", "daemon": daemonData})
        return Response(
            {"detail": "Daemon already running", "daemon": daemonData},
            status=status.HTTP_400_BAD_REQUEST,
        )

    URL_PATH_STOP = "stop"
    URL_NAME_STOP = "stop"

    @action(
        detail=True, methods=["post"], url_path=URL_PATH_STOP, url_name=URL_NAME_STOP
    )
    def stop(self, request: Request, pk: int | None = None) -> Response:
        """Action method stopping the daemon data of the mailbox.

        Args:
            request: The request triggering the action.
            pk: The private key of the daemon. Defaults to None.

        Returns:
            A response detailing the stop result for the daemon.
        """
        daemon = self.get_object()
        daemonData = self.get_serializer(daemon).data
        result = EMailArchiverDaemonRegistry.stopDaemon(daemon)
        if result:
            return Response({"status": "Daemon stopped", "daemon": daemonData})
        return Response(
            {"status": "Daemon not running", "daemon": daemonData},
            status=status.HTTP_400_BAD_REQUEST,
        )

    URL_PATH_LOG_DOWNLOAD = "log/download"
    URL_NAME_LOG_DOWNLOAD = "log-download"

    @action(
        detail=True,
        methods=["get"],
        url_path=URL_PATH_LOG_DOWNLOAD,
        url_name=URL_NAME_LOG_DOWNLOAD,
    )
    def log_download(self, request: Request, pk: int | None = None) -> FileResponse:
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

        number = request.query_params.get("number", "0")
        try:
            number = int(number)
        except ValueError:
            number = 0
        number_suffix = f".{number}" if number > 0 else ""
        daemonLogFilepath = daemon.log_filepath + number_suffix
        if not daemonLogFilepath or not os.path.exists(daemonLogFilepath):
            raise Http404("Log file not found")

        daemonLogFilename = os.path.basename(daemonLogFilepath)
        with open(daemonLogFilepath, "rb") as daemonLogFile:
            return FileResponse(
                daemonLogFile, as_attachment=True, filename=daemonLogFilename
            )
