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

"""Module with the :class:`web.views.DashboardView`."""

from datetime import timedelta
from typing import Any, override

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView

from core.models import Account, Attachment, Correspondent, Daemon, Email, Mailbox


class DashboardView(LoginRequiredMixin, TemplateView):
    """View function for the web dashboard."""

    URL_NAME = "dashboard"
    template_name = "web/dashboard.html"

    @override
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["latest_emails"] = Email.objects.filter(  # type: ignore[misc]  # user auth is checked by LoginRequiredMixin, we also test for this
            mailbox__account__user=self.request.user,
            created__gte=timezone.now() - timedelta(days=1),
        ).order_by(
            "-created"
        )[
            :50
        ]
        context["emails_count"] = Email.objects.filter(  # type: ignore[misc]  # user auth is checked by LoginRequiredMixin, we also test for this
            mailbox__account__user=self.request.user
        ).count()
        context["attachments_count"] = Attachment.objects.filter(  # type: ignore[misc]  # user auth is checked by LoginRequiredMixin, we also test for this
            email__mailbox__account__user=self.request.user
        ).count()
        context["correspondents_count"] = (
            Correspondent.objects.filter(  # type: ignore[misc]  # user auth is checked by LoginRequiredMixin, we also test for this
                user=self.request.user
            ).count()
        )
        context["accounts_count"] = Account.objects.filter(  # type: ignore[misc]  # user auth is checked by LoginRequiredMixin, we also test for this
            user=self.request.user
        ).count()
        context["mailboxes_count"] = Mailbox.objects.filter(  # type: ignore[misc]  # user auth is checked by LoginRequiredMixin, we also test for this
            account__user=self.request.user
        ).count()
        context["daemons_count"] = Daemon.objects.filter(  # type: ignore[misc]  # user auth is checked by LoginRequiredMixin, we also test for this
            mailbox__account__user=self.request.user
        ).count()

        return context
