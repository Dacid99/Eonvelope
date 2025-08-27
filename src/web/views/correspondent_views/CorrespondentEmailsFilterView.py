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

"""Module with the :class:`web.views.CorrespondentEmailsFilterView` view."""

from typing import Any, override

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.views.generic.detail import SingleObjectMixin

from core.models import Correspondent, EmailCorrespondent

from ...filters import CorrespondentEmailFilterSet
from ..base import FilterPageView


class CorrespondentEmailsFilterView(
    LoginRequiredMixin, FilterPageView, SingleObjectMixin
):
    """View for filtering listed :class:`core.models.EmailCorrespondent` instances with a certain correspondent."""

    URL_NAME = "correspondent-emails"
    model = EmailCorrespondent
    template_name = "web/correspondent/correspondent_email_filter_list.html"
    context_object_name = "correspondent_emails"
    filterset_class = CorrespondentEmailFilterSet
    ordering = ["-created"]

    @override
    def get_queryset(self) -> QuerySet[EmailCorrespondent]:
        correspondent_queryset = Correspondent.objects.filter(
            user=self.request.user  # type: ignore[misc]  # user auth is checked by LoginRequiredMixin, we also test for this
        ).distinct()
        self.object = self.get_object(queryset=correspondent_queryset)
        return (
            super()
            .get_queryset()
            .filter(
                email__mailbox__account__user=self.request.user,
                correspondent=self.object,
            )
            .select_related("email")
        )

    @override
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["correspondent"] = self.object
        return context
