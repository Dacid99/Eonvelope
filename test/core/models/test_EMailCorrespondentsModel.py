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


"""Test module for :mod:`core.models.EMailCorrespondentsModel`.

Fixtures:
    :func:`fixture_emailCorrespondentModels`: Creates an :class:`core.models.EMailCorrespondentsModel.EMailCorrespondentsModel` instance for testing.
"""

import pytest
from django.db import IntegrityError
from model_bakery import baker

from core.constants import HeaderFields
from core.models.CorrespondentModel import CorrespondentModel
from core.models.EMailCorrespondentsModel import EMailCorrespondentsModel
from core.models.EMailModel import EMailModel


@pytest.fixture
def mock_CorrespondentModel_fromHeader(mocker, faker):
    fake_CorrespondentModel = CorrespondentModel(email_address=faker.email())
    return mocker.patch(
        "core.models.EMailCorrespondentsModel.CorrespondentModel.fromHeader",
        autospec=True,
        return_value=fake_CorrespondentModel,
    )


@pytest.fixture
def fake_header_name(faker):
    """Fixture providing a random correspondent header name."""
    return faker.random_element(HeaderFields.Correspondents.values)


@pytest.fixture
def fake_header(faker):
    """Fixture providing a random header value."""
    return faker.sentence()


@pytest.mark.django_db
def test_EMailCorrespondentsModel_fields(emailCorrespondentModel):
    """Tests the fields of :class:`core.models.CorrespondentModel.CorrespondentModel`."""

    assert emailCorrespondentModel.email is not None
    assert isinstance(emailCorrespondentModel.email, EMailModel)
    assert emailCorrespondentModel.correspondent is not None
    assert isinstance(emailCorrespondentModel.correspondent, CorrespondentModel)
    assert emailCorrespondentModel.mention is not None
    assert any(
        emailCorrespondentModel.mention == mention
        for mention in HeaderFields.Correspondents.values
    )


@pytest.mark.django_db
def test_EMailCorrespondentsModel___str__(emailCorrespondentModel):
    """Tests the string representation of :class:`core.models.EMailCorrespondentsModel.EMailCorrespondentsModel`."""
    assert str(emailCorrespondentModel.email) in str(emailCorrespondentModel)
    assert str(emailCorrespondentModel.correspondent) in str(emailCorrespondentModel)
    assert str(emailCorrespondentModel.mention) in str(emailCorrespondentModel)


@pytest.mark.django_db
def test_EMailCorrespondentsModel_foreign_key_email_deletion(emailCorrespondentModel):
    """Tests the on_delete foreign key constraint on email in :class:`core.models.EMailCorrespondentsModel.EMailCorrespondentsModel`."""
    emailCorrespondentModel.email.delete()

    with pytest.raises(EMailCorrespondentsModel.DoesNotExist):
        emailCorrespondentModel.refresh_from_db()


@pytest.mark.django_db
def test_EMailCorrespondentsModel_foreign_key_correspondent_deletion(
    emailCorrespondentModel,
):
    """Tests the on_delete foreign key constraint on correspondent in :class:`core.models.EMailCorrespondentsModel.EMailCorrespondentsModel`."""
    emailCorrespondentModel.correspondent.delete()

    with pytest.raises(EMailCorrespondentsModel.DoesNotExist):
        emailCorrespondentModel.refresh_from_db()


@pytest.mark.django_db
def test_EMailCorrespondentsModel_unique_constraints(emailCorrespondentModel):
    """Tests the unique constraint in :class:`core.models.CorrespondentModel.CorrespondentModel`."""
    with pytest.raises(IntegrityError):
        baker.make(
            EMailCorrespondentsModel,
            email=emailCorrespondentModel.email,
            correspondent=emailCorrespondentModel.correspondent,
            mention=emailCorrespondentModel.mention,
        )


@pytest.mark.django_db
def test_EMailCorrespondentsModel_createFromHeader_success(
    emailModel, fake_header_name, fake_header, mock_CorrespondentModel_fromHeader
):
    """Tests :func:`core.models.EMailCorrespondentsModel.EMailCorrespondentsModel.createFromHeader`
    in case of success.
    """
    result = EMailCorrespondentsModel.createFromHeader(
        fake_header, fake_header_name, emailModel
    )

    assert isinstance(result, EMailCorrespondentsModel)
    assert result.pk is not None
    assert result.correspondent is mock_CorrespondentModel_fromHeader.return_value
    assert result.email is emailModel
    assert result.mention is fake_header_name

    mock_CorrespondentModel_fromHeader.assert_called_once_with(fake_header)
    assert result.mention == fake_header_name


@pytest.mark.django_db
def test_EMailCorrespondentsModel_createFromHeader_no_correspondent(
    emailModel, fake_header_name, fake_header, mock_CorrespondentModel_fromHeader
):
    """Tests :func:`core.models.EMailCorrespondentsModel.EMailCorrespondentsModel.createFromHeader`
    in case of the correspondent cannot be set up.
    """
    mock_CorrespondentModel_fromHeader.return_value = None

    result = EMailCorrespondentsModel.createFromHeader(
        fake_header, fake_header_name, emailModel
    )

    assert result is None
    mock_CorrespondentModel_fromHeader.assert_called_once_with(fake_header)


@pytest.mark.django_db
def test_EMailCorrespondentsModel_createFromHeader_no_email(
    fake_header_name, fake_header, mock_CorrespondentModel_fromHeader
):
    """Tests :func:`core.models.EMailCorrespondentsModel.EMailCorrespondentsModel.createFromHeader`
    in case the email argument is not in the database.
    """
    with pytest.raises(ValueError):
        EMailCorrespondentsModel.createFromHeader(
            fake_header, fake_header_name, EMailModel()
        )

    mock_CorrespondentModel_fromHeader.assert_not_called()
