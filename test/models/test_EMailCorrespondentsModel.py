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


"""Test module for :mod:`Emailkasten.Models.EMailCorrespondentsModel`.

Fixtures:
    :func:`fixture_emailCorrespondentsModel`: Creates an :class:`Emailkasten.Models.EMailCorrespondentsModel.EMailCorrespondentsModel` instance for testing.
"""

import pytest
from django.db import IntegrityError
from model_bakery import baker

from Emailkasten.Models.CorrespondentModel import CorrespondentModel
from Emailkasten.Models.EMailCorrespondentsModel import EMailCorrespondentsModel
from Emailkasten.Models.EMailModel import EMailModel


@pytest.fixture(name='emailCorrespondent')
def fixture_emailCorrespondentsModel() -> EMailCorrespondentsModel:
    """Creates an :class:`Emailkasten.Models.EMailModel.EMailModel` instance for testing.

    Returns:
        The emailCorrespondent instance for testing.
    """
    return baker.make(EMailCorrespondentsModel)


@pytest.mark.django_db
def test_CorrespondentModel_creation(emailCorrespondent):
    """Tests the correct default creation of :class:`Emailkasten.Models.CorrespondentModel.CorrespondentModel`."""

    assert emailCorrespondent.email is not None
    assert isinstance(emailCorrespondent.email, EMailModel)
    assert emailCorrespondent.correspondent is not None
    assert isinstance(emailCorrespondent.correspondent, CorrespondentModel)
    assert emailCorrespondent.mention is not None
    assert any(
        emailCorrespondent.mention == mention for mention, _ in EMailCorrespondentsModel.MENTIONTYPES
    )
    assert str(emailCorrespondent.email) in str(emailCorrespondent)
    assert str(emailCorrespondent.correspondent) in str(emailCorrespondent)
    assert str(emailCorrespondent.mention) in str(emailCorrespondent)


@pytest.mark.django_db
def test_EMailModel_foreign_key_email_deletion(emailCorrespondent):
    """Tests the on_delete foreign key constraint on email in :class:`Emailkasten.Models.EMailCorrespondentsModel.EMailCorrespondentsModel`."""

    emailCorrespondent.email.delete()

    with pytest.raises(EMailCorrespondentsModel.DoesNotExist):
        emailCorrespondent.refresh_from_db()


@pytest.mark.django_db
def test_EMailModel_foreign_key_correspondent_deletion(emailCorrespondent):
    """Tests the on_delete foreign key constraint on correspondent in :class:`Emailkasten.Models.EMailCorrespondentsModel.EMailCorrespondentsModel`."""

    emailCorrespondent.correspondent.delete()

    with pytest.raises(EMailCorrespondentsModel.DoesNotExist):
        emailCorrespondent.refresh_from_db()


@pytest.mark.django_db
def test_CorrespondentModel_unique(emailCorrespondent):
    """Tests the unique constraint in :class:`Emailkasten.Models.CorrespondentModel.CorrespondentModel`."""

    with pytest.raises(IntegrityError):
        baker.make(EMailCorrespondentsModel, email=emailCorrespondent.email, correspondent=emailCorrespondent.correspondent, mention=emailCorrespondent.mention)
