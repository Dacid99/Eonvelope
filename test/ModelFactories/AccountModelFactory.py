# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import factory

from Emailkasten.Models.AccountModel import AccountModel

from .UserFactory import UserFactory


class AccountModelFactory(factory.django.DjangoModelFactory):
    """Factory class for :class:`Emailkasten.Models.AccountModel`."""

    class Meta:
        model = AccountModel

    mail_address = factory.Faker("email")
    password = factory.Faker("password")
    mail_host = factory.Faker("domain_name")
    protocol = factory.Faker("random_element", elements = AccountModel.PROTOCOL_CHOICES.keys())
    user = factory.SubFactory(UserFactory)
