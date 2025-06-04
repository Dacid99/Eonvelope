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
from typing import TYPE_CHECKING, Final, override

from django.http import FileResponse, Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.EmailArchiverDaemonRegistry import EmailArchiverDaemonRegistry
from core.models import Daemon

from ..filters import DaemonFilterSet
from ..mixins.NoCreateMixin import NoCreateMixin
from ..serializers import BaseDaemonSerializer


if TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework.request import Request


class DaemonViewSet(NoCreateMixin, viewsets.ModelViewSet[Daemon]):
    """Viewset for the :class:`core.models.Daemon`.

    Provides all but the create method.
    """

    BASENAME = Daemon.BASENAME
    serializer_class = BaseDaemonSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = DaemonFilterSet
    permission_classes = [IsAuthenticated]
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
    def get_queryset(self) -> QuerySet[Daemon]:
        """Filters the data for entries connected to the request user.

        Returns:
            The daemon entries matching the request user.
        """
        if getattr(self, "swagger_fake_view", False):
            return Daemon.objects.none()
        return Daemon.objects.filter(mailbox__account__user=self.request.user)  # type: ignore[misc]  # user auth is checked by LoginRequiredMixin, we also test for this

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

        available_fetching_options = daemon.mailbox.get_available_fetching_criteria()
        return Response({"options": available_fetching_options})

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
        result = EmailArchiverDaemonRegistry.test_daemon(daemon)
        daemon.refresh_from_db()
        daemon_data = self.get_serializer(daemon).data
        return Response(
            {
                "detail": (
                    "Daemon testrun was successful."
                    if result
                    else "Daemon testrun failed!"
                ),
                "daemon": daemon_data,
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
        result = EmailArchiverDaemonRegistry.start_daemon(daemon)
        if result:
            response = Response({"detail": "Daemon started"})
        else:
            response = Response(
                {"detail": "Daemon already running"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        daemon.refresh_from_db()
        daemon_data = self.get_serializer(daemon).data
        response.data["daemon"] = daemon_data
        return response

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
        result = EmailArchiverDaemonRegistry.stop_daemon(daemon)
        if result:
            response = Response({"status": "Daemon stopped"})
        else:
            response = Response(
                {"status": "Daemon not running"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        daemon.refresh_from_db()
        daemon_data = self.get_serializer(daemon).data
        response.data["daemon"] = daemon_data
        return response

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
            Http404: If the filepath is not in the database or it doesn't exist.

        Returns:
            A fileresponse containing the requested file.
        """
        daemon = self.get_object()

        number_query_param = request.query_params.get("number", "0")
        try:
            number = int(number_query_param)
        except ValueError:
            number = 0
        number_suffix = f".{number}" if number > 0 else ""
        daemon_log_filepath = daemon.log_filepath + number_suffix
        if not daemon_log_filepath or not os.path.exists(daemon_log_filepath):
            raise Http404("Log file not found")

        daemon_log_filename = os.path.basename(daemon_log_filepath)
        return FileResponse(
            open(daemon_log_filepath, "rb"),
            as_attachment=True,
            filename=daemon_log_filename,
        )
