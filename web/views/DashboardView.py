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

"""Module with the :func:`web.views.DashboardView.DashboardView`."""

from datetime import timedelta
from typing import Any, override

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView

from core.models.AttachmentModel import AttachmentModel
from core.models.CorrespondentModel import CorrespondentModel
from core.models.EMailModel import EMailModel
from core.models.MailingListModel import MailingListModel


class DashboardView(LoginRequiredMixin, TemplateView):
    """View function for the web dashboard."""

    URL_NAME = "dashboard"
    template_name = "web/dashboard.html"

    @override
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        if not self.request.user.is_authenticated:
            return {}
        context = super().get_context_data(**kwargs)

        context["latest_emails"] = EMailModel.objects.filter(
            mailbox__account__user=self.request.user,
            created__gte=timezone.now() - timedelta(days=1),
        ).order_by("-created")
        context["emails_count"] = EMailModel.objects.filter(
            mailbox__account__user=self.request.user
        ).count()
        context["mailinglists_count"] = (
            MailingListModel.objects.filter(
                emails__mailbox__account__user=self.request.user
            )
            .distinct()
            .count()
        )
        context["attachments_count"] = AttachmentModel.objects.filter(
            email__mailbox__account__user=self.request.user
        ).count()
        context["correspondents_count"] = (
            CorrespondentModel.objects.filter(
                emails__mailbox__account__user=self.request.user
            )
            .distinct()
            .count()
        )

        return context
