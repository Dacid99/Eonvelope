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


"""Test module for :mod:`Emailkasten.Models.CorrespondentModel`."""

import datetime
import pytest

from django.db import IntegrityError

from .ModelFactories.CorrespondentModelFactory import CorrespondentModelFactory


@pytest.mark.django_db
@pytest.mark.parametrize(
    'email_name, email_address',
    [
        ("test name", "test@mail.com"),
        ("", "äöüß123@mail.sh")
    ]
)
def test_CorrespondentModel_creation(email_name: str, email_address: str):
    """Tests the correct creation of :class:`Emailkasten.Models.CorrespondentModel.CorrespondentModel`.

    Args:
        email_name: The email_name parameter.
        email_address: The email_address parameter.
    """
    correspondent = CorrespondentModelFactory(email_name=email_name, email_address=email_address)
    assert correspondent.email_name == email_name
    assert correspondent.email_address == email_address
    assert correspondent.is_favorite is False
    assert isinstance(correspondent.updated, datetime.datetime)
    assert correspondent.updated is not None
    assert isinstance(correspondent.created, datetime.datetime)
    assert correspondent.created is not None
    assert correspondent.email_address in str(correspondent)


@pytest.mark.django_db
def test_CorrespondentModel_unique():
    """Tests the unique constraint in :class:`Emailkasten.Models.CorrespondentModel.CorrespondentModel`"""
    CorrespondentModelFactory(email_name="test name", email_address="test@mail.com")
    with pytest.raises(IntegrityError):
        CorrespondentModelFactory(email_name="another test", email_address="test@mail.com")
