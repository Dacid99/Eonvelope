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

"""Module with the :class:`UploadEmailView` view class."""

from io import BufferedReader
from typing import override

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.views.generic import DetailView
from django.views.generic.edit import FormView

from core.constants import SupportedEmailUploadFormats
from core.models.EMailModel import EMailModel
from core.models.MailboxModel import MailboxModel

from ...forms.UploadEmailForm import UploadEmailForm


class UploadEmailView(LoginRequiredMixin, DetailView, FormView):
    """View for uploading email and mailbox files to a maibox."""

    URL_NAME = MailboxModel.get_upload_web_url_name()
    model = MailboxModel
    context_object_name = "mailbox"
    form_class = UploadEmailForm
    template_name = "web/mailbox/upload_email.html"

    @override
    def get_success_url(self) -> str:
        """Gets the success_url of the upload.

        Returns:
            The detail url of the mailbox.
        """
        return self.object.get_absolute_url()

    @override
    def get_queryset(self) -> QuerySet:
        """Restricts the queryset to objects owned by the requesting user."""
        return MailboxModel.objects.filter(account__user=self.request.user)

    @override
    def form_valid(self, form: UploadEmailForm) -> HttpResponse:
        """Runs when the request form data is valid.

        Args:
            form: The form of the request data.

        Returns:
            A :class:`django.http.HttpResponse` redirecting to :attr:`success_url`.
        """
        file = form.cleaned_data["file"]
        file_format = form.cleaned_data["file_format"]
        self.process_email_file(file_format, file)
        return super().form_valid(form)

    @override
    def form_invalid(self, form: UploadEmailForm) -> HttpResponse:
        """Runs when the request form data is invalid.

        Note:
            This override is required to reconcile :class:`FormView` and :class:`DetailView`.

        Args:
            form: The form of the request data.

        Returns:
            A :class:`django.http.HttpResponse` redirecting to :attr:`success_url`.
        """
        self.object = self.get_object()
        return super().form_invalid(form)

    def process_email_file(self, file_format: str, file: BufferedReader) -> None:
        """Processes the uploaded file.

        Todo:
            Reading the file in chunks to improve memory load.

        Args:
            file_format: The format of the uploaded file.
            file: The uploaded file.
        """
        self.object = self.get_object()
        if file_format == SupportedEmailUploadFormats.EML:
            EMailModel.createFromEmailBytes(file.read(), mailbox=self.object)
        else:
            self.object.addFromMailboxFile(file.read(), file_format)
