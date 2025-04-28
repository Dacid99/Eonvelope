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

"""Module with the :class:`AttachmentFilterView` view."""

from typing import override

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet

from core.models.AttachmentModel import AttachmentModel

from ...filters.AttachmentFilter import AttachmentFilter
from ..FilterPageView import FilterPageView


class AttachmentFilterView(LoginRequiredMixin, FilterPageView):
    """View for filtering listed :class:`core.models.AttachmentModel.AttachmentModel` instances."""

    URL_NAME = AttachmentModel.get_list_web_url_name()
    model = AttachmentModel
    template_name = "web/attachment/attachment_filter_list.html"
    context_object_name = "attachments"
    filterset_class = AttachmentFilter
    paginate_by = 25

    @override
    def get_queryset(self) -> QuerySet[AttachmentModel]:
        """Restricts the queryset to objects owned by the requesting user."""
        if not self.request.user.is_authenticated:
            return AttachmentModel.objects.none()
        return AttachmentModel.objects.filter(
            email__mailbox__account__user=self.request.user
        )
