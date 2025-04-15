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

"""Module with :class:`web.mixins.TestActionMixin.TestActionMixin`."""


from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from core.utils.fetchers.exceptions import MailAccountError, MailboxError


class TestActionMixin:
    """Mixin to provide test button handling for views."""

    def handle_test(self, request: HttpRequest) -> HttpResponse:
        """The handler method for the `test` action."""
        self.object = self.get_object()
        test_result = self.perform_test()
        self.object.refresh_from_db()
        context = self.get_context_data(object=self.object)
        context["test_result"] = test_result
        return render(request, self.template_name, context)

    def perform_test(self) -> dict[str, bool | str]:
        """Handling of the object test.

        Returns:
            Data containing the status and, if provided, the error message of the test.
        """
        result = {"status": None, "error": None}
        try:
            self.object.test_connection()
        except MailAccountError as error:
            result.update({"status": False, "error": str(error)})
        except MailboxError as error:
            result.update({"status": False, "error": str(error)})
        else:
            result.update({"status": True})
        return result
