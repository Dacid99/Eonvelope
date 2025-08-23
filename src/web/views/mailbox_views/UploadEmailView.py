# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Emailkasten Contributors
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

"""Module with the :class:`web.views.UploadEmailView` view class."""

from typing import override

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpResponse
from django.views.generic import DetailView
from django.views.generic.edit import FormView

from core.models import Mailbox

from ...forms.UploadEmailForm import UploadEmailForm


class UploadEmailView(LoginRequiredMixin, DetailView, FormView):
    """View for uploading email and mailbox files to a mailbox."""

    URL_NAME = Mailbox.get_upload_web_url_name()
    model = Mailbox
    context_object_name = "mailbox"
    form_class = UploadEmailForm
    template_name = "web/mailbox/upload_email.html"

    @override
    def get_success_url(self) -> str:
        """Gets the success_url of the upload.

        Returns:
            The detail url of the mailbox.
        """
        return self.object.get_absolute_url()  # type: ignore[no-any-return]  # self.object is set during dispatch via get_queryset().get(), so it is always a Mailbox

    @override
    def get_queryset(self) -> QuerySet[Mailbox]:
        """Restricts the queryset to objects owned by the requesting user."""
        return Mailbox.objects.filter(account__user=self.request.user)  # type: ignore[misc]  # user auth is checked by LoginRequiredMixin, we also test for this

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
        self.object = self.get_object()  # required to reconcile FormView and DetailView
        try:
            self.object.add_emails_from_file(file, file_format)
        except ValueError as error:
            form.add_error("file", str(error))
            return self.form_invalid(form)
        else:
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
