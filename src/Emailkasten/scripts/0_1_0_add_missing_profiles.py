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

"""Script adding missing UserProfile related fields to the existing users.

Used for migration to 0.1.0 .
"""

from django.contrib.auth import get_user_model

from Emailkasten.models import UserProfile


def run():
    print("Adding missing user profiles ...")
    count = 0
    for user in get_user_model().objects.all():
        if not hasattr(user, "profile"):
            UserProfile.objects.create(user=user)
            count += 1
    print(f"Successfully added {count} missing profiles.")
