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

"""Module with the :class:`MailboxViewSet` viewset."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final, override

from django.http import FileResponse, Http404
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import BooleanField, CharField, ChoiceField

from api.utils import query_param_list_to_typed_list
from api.v1.filters import MailboxFilterSet
from api.v1.mixins import ToggleFavoriteMixin
from api.v1.serializers import MailboxWithDaemonSerializer
from api.v1.serializers.UploadEmailSerializer import UploadEmailSerializer
from core.constants import EmailFetchingCriterionChoices, SupportedEmailDownloadFormats
from core.models import Email, Mailbox
from core.utils import FetchingCriterion
from core.utils.fetchers.exceptions import FetcherError

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework.request import Request


@extend_schema_view(
    list=extend_schema(description=_("Lists all instances matching the filter.")),
    retrieve=extend_schema(description=_("Retrieves a single instance.")),
    update=extend_schema(description=_("Updates a single instance.")),
    destroy=extend_schema(description=_("Deletes a single instance.")),
    test=extend_schema(
        request=None,
        responses={
            200: inline_serializer(
                name="test_mailbox_response",
                fields={
                    "detail": CharField(),
                    "result": BooleanField(),
                    "data": MailboxWithDaemonSerializer(),
                },
            )
        },
        description=_("Tests a mailbox."),
    ),
    fetching_options=extend_schema(
        request=None,
        responses={200: OpenApiTypes.JSON_PTR},
        description=_("Lists all available fetching criteria for a mailbox."),
    ),
    fetch=extend_schema(
        request=inline_serializer(
            name="fetch_criterion_data",
            fields={
                "criterion": ChoiceField(choices=EmailFetchingCriterionChoices),
                "criterion_arg": CharField(required=False),
            },
        ),
        responses={
            200: inline_serializer(
                name="fetch_mailbox_response",
                fields={
                    "detail": CharField(),
                    "result": BooleanField(),
                    "data": MailboxWithDaemonSerializer(),
                },
            )
        },
        description=_(
            "Fetches the emails from a mailbox based on the given criterion. Only criteria available for that mailbox are accepted."
        ),
    ),
    download=extend_schema(
        parameters=[
            OpenApiParameter(
                name="file_format",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                enum=SupportedEmailDownloadFormats.values,
            ),
        ],
        request=None,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.BINARY,
                description="content-disposition: attachment",
            )
        },
        description=_("Downloads all emails of a mailbox."),
    ),
    download_batch=extend_schema(
        operation_id="v1_mailboxes_batch_download_retrieve",
        parameters=[
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                explode=True,
                many=True,
                description=_(
                    "A list of integer values identifying the mailboxes. Duplicates are ignored. Accepts both id=1,2,3 and id=1&id=2&id=3 notation"
                ),
            ),
            OpenApiParameter(
                name="file_format",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                enum=SupportedEmailDownloadFormats.values,
            ),
        ],
        request=None,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.BINARY,
                description="content-disposition: attachment",
            )
        },
        description=_("Downloads all emails of multiple mailbox instances."),
    ),
    upload_emails=extend_schema(
        request=UploadEmailSerializer,
        responses={
            200: inline_serializer(
                name="upload_emails_mailbox_response",
                fields={
                    "detail": CharField(),
                    "data": MailboxWithDaemonSerializer(),
                },
            )
        },
        description=_("Upload emails in a file to a mailbox instance."),
    ),
)
class MailboxViewSet(
    viewsets.ReadOnlyModelViewSet[Mailbox],
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    ToggleFavoriteMixin,
):
    """Viewset for the :class:`core.models.Mailbox.Mailbox`.

    Provides all but the create action.
    """

    BASENAME = Mailbox.BASENAME
    serializer_class = MailboxWithDaemonSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = MailboxFilterSet
    permission_classes = [IsAuthenticated]
    ordering_fields: Final[list[str]] = [
        "name",
        "account__mail_address",
        "account__mail_host",
        "account__protocol",
        "save_attachments",
        "save_to_eml",
        "is_favorite",
        "is_healthy",
        "created",
        "updated",
    ]
    ordering: Final[list[str]] = ["id"]

    @override
    def get_queryset(self) -> QuerySet[Mailbox]:
        """Filters the data for entries connected to the request user.

        Returns:
            The mailbox entries matching the request user.
        """
        if getattr(self, "swagger_fake_view", False):
            return Mailbox.objects.none()
        return Mailbox.objects.filter(  # type: ignore[misc]  # user auth is checked by permissions, we also test for this
            account__user=self.request.user
        ).prefetch_related(
            "daemons"
        )

    URL_PATH_TEST = "test"
    URL_NAME_TEST = "test"

    @action(
        detail=True, methods=["post"], url_path=URL_PATH_TEST, url_name=URL_NAME_TEST
    )
    def test(self, request: Request, pk: int | None = None) -> Response:
        """Action method testing the mailbox data.

        Args:
            request: The request triggering the action.
            pk: The private key of the mailbox to test. Defaults to None.

        Returns:
            A response containing the updated mailbox data and the test result.
        """
        mailbox = self.get_object()
        response = Response(
            {
                "detail": _("Tested mailbox"),
            }
        )
        try:
            mailbox.test()
        except FetcherError as error:
            response.data["result"] = False
            response.data["error"] = str(error)
        else:
            response.data["result"] = True
        mailbox.refresh_from_db()
        response.data["data"] = self.get_serializer(mailbox).data
        return response

    URL_PATH_FETCHING_OPTIONS = "fetching-options"
    URL_NAME_FETCHING_OPTIONS = "fetching-options"

    @action(
        detail=True,
        methods=["get"],
        url_path=URL_PATH_FETCHING_OPTIONS,
        url_name=URL_NAME_FETCHING_OPTIONS,
    )
    def fetching_options(self, request: Request, pk: int | None = None) -> Response:
        """Action method returning all fetching options for the mailbox.

        Args:
            request: The request triggering the action.
            pk: int: The private key of the mailbox. Defaults to None.

        Returns:
            A response detailing the request status.
        """
        mailbox = self.get_object()

        available_fetching_options = mailbox.available_fetching_criteria
        return Response({"options": available_fetching_options})

    URL_PATH_FETCH = "fetch"
    URL_NAME_FETCH = "fetch"

    @action(
        detail=True,
        methods=["post"],
        url_path=URL_PATH_FETCH,
        url_name=URL_NAME_FETCH,
    )
    def fetch(self, request: Request, pk: int | None = None) -> Response:
        """Action method fetching all mails from the mailbox.

        Args:
            request: The request triggering the action.
            pk: The private key of the mailbox. Defaults to None.

        Returns:
            A response with the mailbox data.
        """
        mailbox = self.get_object()
        criterion = request.data.get("criterion")
        criterion_arg = request.data.get("criterion_arg", "")
        if not criterion:
            raise ValidationError(
                {"criterion": _("Fetching criterion is required.")},
            )
        if criterion not in mailbox.available_fetching_criteria:
            raise ValidationError(
                {
                    "criterion": _(
                        "The given criterion %(criterion)s is not available for this mailbox."
                    )
                    % {"criterion": criterion}
                },
            )
        fetching_criterion = FetchingCriterion(criterion, criterion_arg)
        try:
            fetching_criterion.validate()
        except ValueError as error:
            raise ValidationError({"criterion_arg": str(error)}) from error
        try:
            mailbox.fetch(fetching_criterion)
        except FetcherError as error:
            response = Response(
                {
                    "detail": _("Error with mailaccount or mailbox occurred."),
                    "error": str(error),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            response = Response({"detail": _("All emails fetched.")})
        mailbox.refresh_from_db()
        response.data["data"] = self.get_serializer(mailbox).data
        return response

    URL_PATH_DOWNLOAD = "download"
    URL_NAME_DOWNLOAD = "download"

    @action(
        detail=True,
        methods=["get"],
        url_path=URL_PATH_DOWNLOAD,
        url_name=URL_NAME_DOWNLOAD,
    )
    def download(
        self, request: Request, pk: int | None = None
    ) -> Response | FileResponse:
        """Action method downloading the eml files of all emails in the mailbox in a single file.

        Args:
            request: The request triggering the action.
            pk: The private key of the attachment to download. Defaults to None.

        Raises:
            Http404: If there are no emails in the mailbox.
            ValidationError: If file_format is missing or unsupported.

        Returns:
            A fileresponse containing the emails in the requested format.
        """
        file_format = request.query_params.get("file_format", None)
        if not file_format:
            raise ValidationError(
                {"file_format": _("File format is required.")},
            )
        mailbox = self.get_object()
        try:
            file = Email.queryset_as_file(mailbox.emails.all(), file_format)
        except ValueError:
            raise ValidationError(
                {
                    "file_format": _("File format %(file_format)s is not supported.")
                    % {"file_format": file_format}
                },
            ) from None
        except Email.DoesNotExist:
            raise Http404(_("No emails found.")) from None
        return FileResponse(
            file,
            as_attachment=True,
            filename=mailbox.name + "." + file_format.split("[", maxsplit=1)[0],
        )

    URL_PATH_DOWNLOAD_BATCH = "download"
    URL_NAME_DOWNLOAD_BATCH = "download-batch"

    @action(
        detail=False,
        methods=["get"],
        url_path=URL_PATH_DOWNLOAD_BATCH,
        url_name=URL_NAME_DOWNLOAD_BATCH,
    )
    def download_batch(self, request: Request) -> Response | FileResponse:
        """Action method downloading a batch of mailboxes.

        Todo:
            Validation and parsing of queryparams can probably be done more concisely with a serializer.

        Args:
            request: The request triggering the action.

        Raises:
            Http404: If there are no emails in the mailbox.
            ValidationError: If id or file_format param is missing or in invalid format or file_format is unsupported.

        Returns:
            A fileresponse containing the mailboxes emails in the requested format.
        """
        file_format = request.query_params.get("file_format", None)
        if not file_format:
            raise ValidationError(
                {"file_format": _("File format is required.")},
            )
        requested_id_query_params = request.query_params.getlist("id", [])
        if not requested_id_query_params:
            raise ValidationError(
                {"id": _("Mailbox ids are required.")},
            )
        try:
            requested_ids = query_param_list_to_typed_list(
                requested_id_query_params, int
            )
        except ValueError:
            raise ValidationError(
                {"id": _("Mailbox ids given in invalid format.")},
            ) from None
        try:
            file = Mailbox.queryset_as_file(
                self.get_queryset().filter(pk__in=requested_ids), file_format
            )
        except ValueError:
            raise ValidationError(
                {
                    "file_format": _("File format %(file_format)s is not supported.")
                    % {"file_format": file_format}
                },
            ) from None
        except Mailbox.DoesNotExist:
            raise Http404(_("No mailboxes found")) from None
        return FileResponse(
            file,
            as_attachment=True,
            filename=f"mailboxes_{requested_ids}.zip",
        )

    URL_PATH_UPLOAD_MAILBOX = "upload"
    URL_NAME_UPLOAD_MAILBOX = "upload"

    @action(
        detail=True,
        methods=["post"],
        url_path=URL_PATH_UPLOAD_MAILBOX,
        url_name=URL_NAME_UPLOAD_MAILBOX,
    )
    def upload_emails(self, request: Request, pk: int | None = None) -> Response:
        """Action method allowing upload of a mailbox file and adding the contained mails to a mailbox.

        Args:
            request: The request triggering the action.
            pk: int: The private key of the mailbox to upload to. Defaults to None.

        Returns:
            A response detailing the request status.
        """
        mailbox = (
            self.get_object()
        )  # this must be called first to return 404 for missing authentication even if the data is invalid
        upload_serializer = UploadEmailSerializer(data=request.data)
        upload_serializer.is_valid(raise_exception=True)
        try:
            mailbox.add_emails_from_file(
                upload_serializer.validated_data["file"],
                upload_serializer.validated_data["file_format"],
            )
        except ValueError as error:
            raise ValidationError(
                {"file": str(error)},
            ) from None
        mailbox_serializer = self.get_serializer(mailbox)
        return Response(
            {
                "detail": _("Successfully uploaded mailbox file."),
                "data": mailbox_serializer.data,
            }
        )
