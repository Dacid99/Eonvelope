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

"""Module with the :class:`DaemonViewSet` viewset."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final, override

from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.v1.filters import DaemonFilterSet
from api.v1.serializers import BaseDaemonSerializer
from core.models import Daemon

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework.request import Request


@extend_schema_view(
    list=extend_schema(description="Lists all instances matching the filter."),
    retrieve=extend_schema(description="Retrieves a single instance."),
    update=extend_schema(
        description="Updates a single instance. You must specify format 'json'."
    ),
    create=extend_schema(
        description="Creates a new instance. You must specify format 'json'."
    ),
    destroy=extend_schema(description="Deletes a single instance."),
    test=extend_schema(
        request=None,
        responses={
            200: inline_serializer(
                name="test_daemon_response",
                fields={
                    "detail": OpenApiTypes.STR,
                    "result": OpenApiTypes.BOOL,
                    "data": BaseDaemonSerializer,
                },
            )
        },
        description="Tests the daemon instance.",
    ),
    start=extend_schema(
        request=None,
        description="Starts the daemon instances periodic task.",
    ),
    stop=extend_schema(
        request=None,
        description="Stops the daemon instances periodic task.",
    ),
)
class DaemonViewSet(viewsets.ModelViewSet[Daemon]):
    """Viewset for the :class:`core.models.Daemon`.

    Provides all CRUD actions.

    Note:
        To update instances the user must specify format "json" with the request.
    """

    BASENAME = Daemon.BASENAME
    serializer_class = BaseDaemonSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = DaemonFilterSet
    permission_classes = [IsAuthenticated]
    ordering_fields: Final[list[str]] = [
        "fetching_criterion",
        "interval__every",
        "interval__period",
        "celery_task__last_run_at",
        "celery_task__total_run_count",
        "is_healthy",
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
        return Daemon.objects.filter(  # type: ignore[misc]  # user auth is checked by permissions, we also test for this
            mailbox__account__user=self.request.user
        ).select_related(
            "interval", "celery_task"
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
        response = Response(
            {
                "detail": _("Tested routine"),
            }
        )
        try:
            daemon.test()
        except Exception as error:
            response.data["result"] = False
            response.data["error"] = str(error)
        else:
            response.data["result"] = True
        daemon.refresh_from_db()
        response.data["data"] = self.get_serializer(daemon).data
        return response

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
        result = daemon.start()
        if result:
            response = Response({"detail": _("Routine started")})
        else:
            response = Response(
                {"detail": _("Routine is already running")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        daemon.refresh_from_db()
        daemon_data = self.get_serializer(daemon).data
        response.data["data"] = daemon_data
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
        result = daemon.stop()
        if result:
            response = Response({"status": _("Routine stopped")})
        else:
            response = Response(
                {"status": _("Routine not running")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        daemon.refresh_from_db()
        daemon_data = self.get_serializer(daemon).data
        response.data["data"] = daemon_data
        return response
