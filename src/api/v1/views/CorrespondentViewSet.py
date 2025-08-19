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

"""Module with the :class:`CorrespondentViewSet` viewset."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final, override

from django.db.models import Prefetch
from django.http import FileResponse, Http404
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.openapi import OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.utils import query_param_list_to_typed_list
from api.v1.mixins.ToggleFavoriteMixin import ToggleFavoriteMixin
from core.models import Correspondent, EmailCorrespondent

from ..filters import CorrespondentFilterSet
from ..serializers import BaseCorrespondentSerializer, CorrespondentSerializer


if TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework.request import Request
    from rest_framework.serializers import BaseSerializer


class CorrespondentViewSet(
    viewsets.ReadOnlyModelViewSet[Correspondent],
    mixins.DestroyModelMixin,
    ToggleFavoriteMixin,
):
    """Viewset for the :class:`core.models.Correspondent.Correspondent`.

    Provides every read-only and a destroy action.
    """

    BASENAME = Correspondent.BASENAME
    serializer_class = CorrespondentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = CorrespondentFilterSet
    permission_classes = [IsAuthenticated]
    ordering_fields: Final[list[str]] = [
        "email_name",
        "email_address",
        "is_favorite",
        "created",
        "updated",
    ]
    ordering: Final[list[str]] = ["id"]

    @override
    def get_queryset(self) -> QuerySet[Correspondent]:
        """Filters the data for entries connected to the request user.

        Returns:
            The correspondent entries matching the request user.
        """
        if getattr(self, "swagger_fake_view", False):
            return Correspondent.objects.none()
        return (
            Correspondent.objects.filter(  # type: ignore[misc]  # user auth is checked by LoginRequiredMixin, we also test for this
                user=self.request.user
            )
            .distinct()
            .prefetch_related(
                Prefetch(
                    "correspondentemails",
                    queryset=EmailCorrespondent.objects.filter(  # type: ignore[misc]  # user auth is checked by LoginRequiredMixin, we also test for this
                        email__mailbox__account__user=self.request.user
                    ).select_related(
                        "email"
                    ),
                )
            )
        )

    @override
    def get_serializer_class(self) -> type[BaseSerializer[Correspondent]]:
        """Sets the serializer for `list` requests to the simplified version."""
        if self.action == "list":
            return BaseCorrespondentSerializer
        return super().get_serializer_class()

    URL_PATH_DOWNLOAD = "download"
    URL_NAME_DOWNLOAD = "download"

    @action(
        detail=True,
        methods=["get"],
        url_path=URL_PATH_DOWNLOAD,
        url_name=URL_NAME_DOWNLOAD,
    )
    def download(self, request: Request, pk: int | None = None) -> FileResponse:
        """Action method downloading the correspondent.

        Args:
            request: The request triggering the action.
            pk: The private key of the correspondent to download. Defaults to None.

        Raises:
            Http404: If the filepath is not in the database or it doesn't exist.

        Returns:
            A fileresponse containing the requested file.
        """
        correspondent = self.get_object()
        return FileResponse(
            Correspondent.queryset_as_file(
                Correspondent.objects.filter(id=correspondent.id)
            ),
            as_attachment=True,
            filename=correspondent.name.replace(" ", "_") + ".vcf",
        )

    URL_PATH_DOWNLOAD_BATCH = "download"
    URL_NAME_DOWNLOAD_BATCH = "download-batch"

    @extend_schema(
        parameters=[OpenApiParameter("id", OpenApiTypes.INT, OpenApiParameter.QUERY)]
    )
    @action(
        detail=False,
        methods=["get"],
        url_path=URL_PATH_DOWNLOAD_BATCH,
        url_name=URL_NAME_DOWNLOAD_BATCH,
    )
    def download_batch(self, request: Request) -> Response | FileResponse:
        """Action method downloading a batch of correspondents.

        Args:
            request: The request triggering the action.

        Raises:
            Http404: If no downloadable correspondent has been requested.

        Returns:
            A fileresponse containing the requested file.
            A 400 response if the id param is missing in the request.
        """
        requested_id_query_params = request.query_params.getlist("id", [])
        if not requested_id_query_params:
            return Response(
                {"detail": _("Correspondent ids missing in request.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            requested_ids = query_param_list_to_typed_list(
                requested_id_query_params, int
            )
        except ValueError:
            return Response(
                {"detail": _("Correspondent ids given in invalid format.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            file = Correspondent.queryset_as_file(
                self.get_queryset().filter(pk__in=requested_ids)
            )
        except Correspondent.DoesNotExist:
            raise Http404(_("No correspondents found")) from None
        return FileResponse(
            file,
            as_attachment=True,
            filename="correspondents.vcf",
        )
