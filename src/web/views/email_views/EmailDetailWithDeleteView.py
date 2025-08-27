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

"""Module with the :class:`web.views.EmailDetailWithDeleteView` view."""

from typing import override

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch, QuerySet
from django.urls import reverse_lazy

from core.models import Email, EmailCorrespondent

from ..base import DetailWithDeleteView
from .EmailFilterView import EmailFilterView


class EmailDetailWithDeleteView(LoginRequiredMixin, DetailWithDeleteView):
    """View for a single :class:`core.models.Email` instance."""

    URL_NAME = Email.get_detail_web_url_name()
    model = Email
    template_name = "web/email/email_detail.html"
    success_url = reverse_lazy("web:" + EmailFilterView.URL_NAME)

    @override
    def get_queryset(self) -> QuerySet[Email]:
        """Restricts the queryset to objects owned by the requesting user."""
        return (
            super()
            .get_queryset()
            .filter(mailbox__account__user=self.request.user)
            .select_related("mailbox", "mailbox__account")
            .prefetch_related(
                "attachments", "in_reply_to", "replies", "references", "referenced_by"
            )
            .prefetch_related(
                Prefetch(
                    "emailcorrespondents",
                    queryset=EmailCorrespondent.objects.select_related("correspondent"),
                )
            )
        )
