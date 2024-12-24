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


"""Test module for :mod:`Emailkasten.Models.CorrespondentModel`."""

import datetime
from model_bakery import baker
import pytest

from django.db import IntegrityError

from Emailkasten.Models.CorrespondentModel import CorrespondentModel

@pytest.mark.django_db
def test_CorrespondentModel_creation():
    """Tests the correct default creation of :class:`Emailkasten.Models.CorrespondentModel.CorrespondentModel`."""

    correspondent = baker.make(CorrespondentModel)
    assert correspondent.email_name is not None
    assert isinstance(correspondent.email_name, str)
    assert correspondent.email_address is not None
    assert isinstance(correspondent.email_address, str)
    assert correspondent.is_favorite is False
    assert correspondent.updated is not None
    assert isinstance(correspondent.updated, datetime.datetime)
    assert correspondent.created is not None
    assert isinstance(correspondent.created, datetime.datetime)

    assert correspondent.email_address in str(correspondent)


@pytest.mark.django_db
def test_CorrespondentModel_unique():
    """Tests the unique constraint in :class:`Emailkasten.Models.CorrespondentModel.CorrespondentModel`."""

    baker.make(CorrespondentModel, email_name="test name", email_address="test@mail.com")
    with pytest.raises(IntegrityError):
        baker.make(CorrespondentModel, email_name="another test", email_address="test@mail.com")
