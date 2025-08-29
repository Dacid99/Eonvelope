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

"""Test module for :mod:`core.models.Email`."""

from __future__ import annotations

import datetime
import os
from io import BytesIO
from tempfile import TemporaryDirectory, gettempdir
from zipfile import ZipFile

import django.db.models
import pytest
from django.core.files.storage import default_storage
from django.db import IntegrityError
from django.urls import reverse
from model_bakery import baker

from core.constants import (
    HeaderFields,
    SupportedEmailDownloadFormats,
    file_format_parsers,
)
from core.models import Correspondent, Email, Mailbox
from Emailkasten.utils.workarounds import get_config

from ...conftest import TEST_EMAIL_PARAMETERS
from .test_Attachment import mock_Attachment_save_to_storage


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    """Mocks :attr:`core.models.Email.logger` of the module."""
    return mocker.patch("core.models.Email.logger", autospec=True)


@pytest.fixture
def spy_save(mocker):
    """Fixture spying on :func:`django.db.models.Model.save`."""
    return mocker.spy(django.db.models.Model, "save")


@pytest.fixture
def mock_Email_save_eml_to_storage(mocker):
    """Fixture patching :func:`core.models.Email.Email.save_eml_to_storage`."""
    return mocker.patch("core.models.Email.Email.save_eml_to_storage", autospec=True)


@pytest.mark.django_db
def test_Email_fields(fake_email):
    """Tests the fields of :class:`core.models.Email.Email`."""

    assert fake_email.message_id is not None
    assert isinstance(fake_email.message_id, str)
    assert fake_email.datetime is not None
    assert isinstance(fake_email.datetime, datetime.datetime)
    assert fake_email.email_subject is not None
    assert isinstance(fake_email.email_subject, str)
    assert fake_email.plain_bodytext is not None
    assert isinstance(fake_email.plain_bodytext, str)
    assert fake_email.html_bodytext is not None
    assert isinstance(fake_email.html_bodytext, str)
    assert fake_email.datasize is not None
    assert isinstance(fake_email.datasize, int)
    assert fake_email.eml_filepath is None
    assert fake_email.html_version is not None
    assert isinstance(fake_email.html_version, str)
    assert fake_email.is_favorite is False

    assert fake_email.mailbox is not None
    assert isinstance(fake_email.mailbox, Mailbox)
    assert fake_email.headers is None
    assert fake_email.x_spam is not None
    assert isinstance(fake_email.x_spam, str)

    assert isinstance(fake_email.updated, datetime.datetime)
    assert fake_email.updated is not None
    assert isinstance(fake_email.created, datetime.datetime)
    assert fake_email.created is not None


@pytest.mark.django_db
def test_Email___str__(fake_email):
    """Tests the string representation of :class:`core.models.Email.Email`."""
    assert fake_email.message_id in str(fake_email)
    assert str(fake_email.datetime) in str(fake_email)
    assert str(fake_email.mailbox) in str(fake_email)


@pytest.mark.django_db
def test_Email_foreign_key_mailbox_deletion(fake_email):
    """Tests the on_delete foreign key constraint on mailbox in :class:`core.models.Email.Email`."""

    fake_email.mailbox.delete()

    with pytest.raises(Email.DoesNotExist):
        fake_email.refresh_from_db()


@pytest.mark.django_db
def test_Email_m2m_references_deletion(fake_email):
    """Tests the on_delete foreign key constraint on in_reply_to in :class:`core.models.Email.Email`."""

    referenced_email = baker.make(Email, x_spam="NO")
    fake_email.references.add(referenced_email)

    referenced_email.delete()

    fake_email.refresh_from_db()
    assert not fake_email.references.exists()
    with pytest.raises(Email.DoesNotExist):
        referenced_email.refresh_from_db()


@pytest.mark.django_db
def test_Email_m2m_in_reply_to_deletion(fake_email):
    """Tests the on_delete foreign key constraint on in_reply_to in :class:`core.models.Email.Email`."""

    in_reply_to_email = baker.make(Email, x_spam="NO")
    fake_email.in_reply_to.add(in_reply_to_email)

    in_reply_to_email.delete()

    fake_email.refresh_from_db()
    assert not fake_email.in_reply_to.exists()
    with pytest.raises(Email.DoesNotExist):
        in_reply_to_email.refresh_from_db()


@pytest.mark.django_db
def test_Email_unique_constraints():
    """Tests the unique constraints of :class:`core.models.Email.Email`."""

    email_1 = baker.make(Email, message_id="abc123")
    email_2 = baker.make(Email, message_id="abc123")
    assert email_1.message_id == email_2.message_id
    assert email_1.mailbox != email_2.mailbox

    mailbox = baker.make(Mailbox)

    email_1 = baker.make(Email, mailbox=mailbox)
    email_2 = baker.make(Email, mailbox=mailbox)
    assert email_1.message_id != email_2.message_id
    assert email_1.mailbox == email_2.mailbox

    baker.make(Email, message_id="abc123", mailbox=mailbox)
    with pytest.raises(IntegrityError):
        baker.make(Email, message_id="abc123", mailbox=mailbox)


@pytest.mark.django_db
def test_Email_delete_emailfiles_success(fake_email_with_file, mock_logger):
    """Tests :func:`core.models.Email.Email.delete`
    if the file removal is successful.
    """
    previous_eml_filepath = fake_email_with_file.eml_filepath

    fake_email_with_file.delete()

    with pytest.raises(Email.DoesNotExist):
        fake_email_with_file.refresh_from_db()
    assert not default_storage.exists(previous_eml_filepath)


@pytest.mark.django_db
def test_Email_delete_email_delete_error(mocker, fake_email_with_file, mock_logger):
    """Tests :func:`core.models.Email.Email.delete`
    if delete raises an exception.
    """
    mock_delete = mocker.patch(
        "core.models.Email.models.Model.delete",
        autospec=True,
        side_effect=AssertionError,
    )

    with pytest.raises(AssertionError):
        fake_email_with_file.delete()

    assert default_storage.exists(fake_email_with_file.eml_filepath)
    mock_delete.assert_called_once()
    mock_logger.debug.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "save_to_eml, expected_save_eml_to_storage_call",
    [
        (True, True),
        (False, False),
    ],
)
def test_Email_save_with_data_success(
    fake_email,
    mock_message,
    spy_save,
    mock_Email_save_eml_to_storage,
    save_to_eml,
    expected_save_eml_to_storage_call,
):
    """Tests :func:`core.models.Email.Email.save`
    in case of success with data to be saved.
    """
    fake_email.mailbox.save_to_eml = save_to_eml

    fake_email.save(email_data=mock_message)

    spy_save.assert_called_once_with(fake_email)
    if expected_save_eml_to_storage_call:
        mock_Email_save_eml_to_storage.assert_called_with(fake_email, mock_message)
    else:
        mock_Email_save_eml_to_storage.assert_not_called()


@pytest.mark.django_db
def test_Email_save_no_data(
    fake_email,
    spy_save,
    mock_Email_save_eml_to_storage,
):
    """Tests :func:`core.models.Email.Email.save`
    in case of success without data to be saved.
    """
    fake_email.mailbox.save_to_eml = True

    fake_email.save()

    spy_save.assert_called_once_with(fake_email)
    mock_Email_save_eml_to_storage.assert_not_called()


@pytest.mark.django_db
def test_Email_save_with_data_failure(
    fake_email,
    mock_message,
    spy_save,
    mock_Email_save_eml_to_storage,
):
    """Tests :func:`core.models.Email.Email.save`
    in case of success saving data fails with an exception.
    """
    mock_Email_save_eml_to_storage.side_effect = AssertionError
    fake_email.mailbox.save_to_eml = True

    with pytest.raises(AssertionError):
        fake_email.save(email_data=mock_message)

    spy_save.assert_called()
    mock_Email_save_eml_to_storage.assert_called()


@pytest.mark.django_db
def test_save_eml_to_storage_success(
    fake_fs,
    fake_file_bytes,
    fake_email,
    mock_logger,
):
    fake_email.eml_filepath = None

    fake_email.save_eml_to_storage(fake_file_bytes)

    fake_email.refresh_from_db()
    assert (
        os.path.basename(fake_email.eml_filepath)
        == str(fake_email.pk) + "_" + fake_email.message_id + ".eml"
    )
    assert default_storage.exists(fake_email.eml_filepath)
    assert default_storage.open(fake_email.eml_filepath).read() == fake_file_bytes
    mock_logger.debug.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_save_eml_to_storage_file_path_set(
    faker,
    fake_fs,
    fake_file_bytes,
    fake_email,
    mock_logger,
):
    fake_email.eml_filepath = default_storage.save(
        faker.file_name(), BytesIO(fake_file_bytes)
    )
    previous_file_path = fake_email.eml_filepath

    fake_email.save_eml_to_storage(fake_file_bytes)

    assert fake_email.eml_filepath == previous_file_path
    assert default_storage.exists(previous_file_path)
    mock_logger.debug.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize("start_id", [1, 2, 3, 4, 5, 6, 7, 8])
def test_Email_conversation(fake_email_conversation, start_id):
    """Tests :func:`core.models.Email.Email.conversation`."""
    start_email = Email.objects.get(id=start_id)

    conversation_emails = start_email.conversation

    assert len(conversation_emails) == 8


@pytest.mark.django_db
@pytest.mark.parametrize(
    "x_spam, expected_result",
    [
        (None, False),
        ("", False),
        ("YES", True),
        ("NO", False),
        ("NO, YES", True),
        ("YES, YES", True),
        ("NO, NO", False),
        ("CRAZY", False),
    ],
)
def test_Email_is_spam(fake_email, x_spam, expected_result):
    """Tests :func:`core.models.Email.Email.is_spam`."""
    fake_email.x_spam = x_spam

    result = fake_email.is_spam

    assert result is expected_result


@pytest.mark.django_db
def test_Email_queryset_as_file_zip_eml(fake_file, fake_email, fake_email_with_file):
    assert Email.objects.count() == 2

    result = Email.queryset_as_file(
        Email.objects.all(), SupportedEmailDownloadFormats.ZIP_EML
    )

    assert Email.objects.count() == 2
    assert hasattr(result, "read")
    with ZipFile(result) as zipfile:
        assert zipfile.namelist() == [
            os.path.basename(fake_email_with_file.eml_filepath)
        ]
        with zipfile.open(
            os.path.basename(fake_email_with_file.eml_filepath)
        ) as zipped_file:
            assert (
                zipped_file.read().replace(b"\r", b"").strip()
                == default_storage.open(fake_email_with_file.eml_filepath)
                .read()
                .replace(b"\r", b"")
                .strip()
            )
    assert hasattr(result, "close")
    result.close()
    assert os.listdir(gettempdir()) == []


@pytest.mark.django_db
@pytest.mark.parametrize(
    "file_format",
    [
        SupportedEmailDownloadFormats.MBOX,
        SupportedEmailDownloadFormats.MMDF,
        SupportedEmailDownloadFormats.BABYL,
        SupportedEmailDownloadFormats.MBOX.title(),
        SupportedEmailDownloadFormats.MMDF.title(),
        SupportedEmailDownloadFormats.BABYL.title(),
    ],
)
def test_Email_queryset_as_file_mailbox_file(
    fake_file, fake_email, fake_email_with_file, file_format
):
    assert Email.objects.count() == 2

    result = Email.queryset_as_file(Email.objects.all(), file_format)

    assert Email.objects.count() == 2
    assert hasattr(result, "read")
    assert hasattr(result, "name")
    parser_class = file_format_parsers[file_format.lower()]
    parser = parser_class(result.name)
    assert len(list(parser.iterkeys())) == 1
    for key in parser.iterkeys():
        assert (
            parser.get_bytes(key).replace(b"\r", b"").strip()
            == default_storage.open(fake_email_with_file.eml_filepath)
            .read()
            .replace(b"\r", b"")
            .strip()
        )
    assert hasattr(result, "close")
    result.close()
    assert os.listdir(gettempdir()) == []


@pytest.mark.django_db
@pytest.mark.parametrize(
    "file_format",
    [
        SupportedEmailDownloadFormats.MAILDIR,
        SupportedEmailDownloadFormats.MH,
        SupportedEmailDownloadFormats.MAILDIR.title(),
        SupportedEmailDownloadFormats.MH.title(),
    ],
)
def test_Email_queryset_as_file_mailbox_zip(
    fake_file, fake_email, fake_email_with_file, file_format
):
    assert Email.objects.count() == 2

    result = Email.queryset_as_file(Email.objects.all(), file_format)

    assert Email.objects.count() == 2
    assert hasattr(result, "read")
    with TemporaryDirectory() as tempdir:
        with ZipFile(result) as zipfile:
            zipfile.extractall(tempdir)
        parser_class = file_format_parsers[file_format.lower()]
        parser = parser_class(os.path.join(tempdir, os.listdir(tempdir)[0]))
        assert len(list(parser.iterkeys())) == 1
        for key in parser.iterkeys():
            assert (
                parser.get_bytes(key).replace(b"\r", b"").strip()
                == default_storage.open(fake_email_with_file.eml_filepath)
                .read()
                .replace(b"\r", b"")
                .strip()
            )
    assert hasattr(result, "close")
    result.close()
    assert os.listdir(gettempdir()) == []


@pytest.mark.django_db
def test_Email_queryset_as_file_mailbox_bad_format(fake_email):
    assert Email.objects.count() == 1

    with pytest.raises(ValueError):
        Email.queryset_as_file(Email.objects.all(), "unSupPortEd")

    assert Email.objects.count() == 1


@pytest.mark.django_db
def test_Email_queryset_as_file_mailbox_empty_queryset():
    assert Email.objects.count() == 0

    with pytest.raises(Email.DoesNotExist):
        Email.queryset_as_file(
            Email.objects.none(), SupportedEmailDownloadFormats.ZIP_EML
        )

    assert Email.objects.count() == 0


@pytest.mark.django_db
def test_Email_add_in_reply_to_no_header(fake_email):
    fake_email.headers = {}

    assert fake_email.in_reply_to.count() == 0

    fake_email.add_in_reply_to()

    assert fake_email.in_reply_to.count() == 0


@pytest.mark.django_db
def test_Email_add_in_reply_to_no_match(faker, fake_email):
    fake_message_id = faker.name()
    fake_email.headers = {"in-reply-to": fake_message_id}

    assert fake_email.in_reply_to.count() == 0

    fake_email.add_in_reply_to()

    assert fake_email.in_reply_to.count() == 0


@pytest.mark.django_db
def test_Email_add_in_reply_to_single(faker, fake_email):
    fake_message_id = faker.name()
    fake_in_reply_to_email = baker.make(
        Email, message_id=fake_message_id, mailbox=fake_email.mailbox
    )
    fake_email.headers = {"in-reply-to": fake_message_id}

    assert fake_email.in_reply_to.count() == 0

    fake_email.add_in_reply_to()

    assert fake_email.in_reply_to.count() == 1
    assert fake_in_reply_to_email in fake_email.in_reply_to.all()


@pytest.mark.django_db
def test_Email_add_in_reply_to_other_email(fake_email, fake_other_email):
    fake_email.headers = {"in-reply-to": fake_other_email.message_id}

    assert fake_email.in_reply_to.count() == 0

    fake_email.add_in_reply_to()

    assert fake_email.in_reply_to.count() == 0


@pytest.mark.django_db
def test_Email_add_in_reply_to_multi(faker, fake_email):
    fake_message_id = faker.name()
    fake_mailbox_2 = baker.make(Mailbox, account=fake_email.mailbox.account)
    fake_referenced_email_1 = baker.make(
        Email, message_id=fake_message_id, mailbox=fake_email.mailbox
    )
    fake_referenced_email_2 = baker.make(
        Email, message_id=fake_message_id, mailbox=fake_mailbox_2
    )
    fake_email.headers = {"in-reply-to": fake_message_id}

    assert fake_email.in_reply_to.count() == 0

    fake_email.add_in_reply_to()

    assert fake_email.in_reply_to.count() == 2
    assert fake_referenced_email_1 in fake_email.in_reply_to.all()
    assert fake_referenced_email_2 in fake_email.in_reply_to.all()


@pytest.mark.django_db
def test_Email_add_references_no_header(fake_email):
    fake_email.headers = {}

    assert fake_email.references.count() == 0

    fake_email.add_references()

    assert fake_email.references.count() == 0


@pytest.mark.django_db
def test_Email_add_references_no_match(faker, fake_email):
    fake_message_id = faker.word()
    fake_email.headers = {"references": fake_message_id}

    assert fake_email.references.count() == 0

    fake_email.add_references()

    assert fake_email.references.count() == 0


@pytest.mark.django_db
def test_Email_add_references_single(faker, fake_email):
    fake_message_id = faker.word()
    fake_referenced_email = baker.make(
        Email, message_id=fake_message_id, mailbox=fake_email.mailbox
    )
    fake_email.headers = {"references": fake_message_id}

    assert fake_email.references.count() == 0

    fake_email.add_references()

    assert fake_email.references.count() == 1
    assert fake_referenced_email in fake_email.references.all()


@pytest.mark.django_db
def test_Email_add_references_other_email(fake_email, fake_other_email):
    fake_email.headers = {"references": fake_other_email.message_id}

    assert fake_email.references.count() == 0

    fake_email.add_references()

    assert fake_email.references.count() == 0


@pytest.mark.django_db
def test_Email_add_references_multi(faker, fake_email):
    fake_message_id_1 = faker.word()
    fake_message_id_2 = faker.word()
    fake_referenced_email_1 = baker.make(
        Email, message_id=fake_message_id_1, mailbox=fake_email.mailbox
    )
    fake_referenced_email_2 = baker.make(
        Email, message_id=fake_message_id_2, mailbox=fake_email.mailbox
    )
    fake_email.headers = {
        "references": fake_message_id_1 + ", " + fake_message_id_2 + "  "
    }

    assert fake_email.references.count() == 0

    fake_email.add_references()

    assert fake_email.references.count() == 2
    assert fake_referenced_email_1 in fake_email.references.all()
    assert fake_referenced_email_2 in fake_email.references.all()


@pytest.mark.django_db
def test_Email_add_correspondents_none(fake_email):
    fake_email.headers = {}

    assert fake_email.correspondents.count() == 0

    fake_email.add_correspondents()

    assert fake_email.correspondents.count() == 0


@pytest.mark.django_db
def test_Email_add_correspondents_other_user(faker, fake_email):
    fake_email_address = faker.email()
    fake_mention = faker.random_element(HeaderFields.Correspondents.values)
    fake_mentioned_correspondent = baker.make(
        Correspondent,
        email_address=fake_email_address,
    )
    fake_email.headers = {fake_mention: fake_email_address}

    assert Correspondent.objects.count() == 1
    assert fake_email.correspondents.count() == 0

    fake_email.add_correspondents()

    assert Correspondent.objects.count() == 2
    assert fake_email.correspondents.count() == 1
    assert fake_mentioned_correspondent not in fake_email.correspondents.all()


@pytest.mark.django_db
def test_Email_add_correspondents_single_in_db(faker, fake_email):
    fake_email_address = faker.email()
    fake_mention = faker.random_element(HeaderFields.Correspondents.values)
    fake_mentioned_correspondent = baker.make(
        Correspondent,
        email_address=fake_email_address,
        user=fake_email.mailbox.account.user,
    )
    fake_email.headers = {fake_mention: fake_email_address}

    assert Correspondent.objects.count() == 1
    assert fake_email.correspondents.count() == 0

    fake_email.add_correspondents()

    assert Correspondent.objects.count() == 1
    assert fake_email.correspondents.count() == 1
    assert (
        fake_email.emailcorrespondents.filter(mention=fake_mention).get().correspondent
        == fake_mentioned_correspondent
    )


@pytest.mark.django_db
def test_Email_add_correspondents_single_not_in_db(faker, fake_email):
    fake_email_address = faker.email()
    fake_mention = faker.random_element(HeaderFields.Correspondents.values)
    fake_email.headers = {fake_mention: fake_email_address}

    assert Correspondent.objects.count() == 0
    assert fake_email.correspondents.count() == 0

    fake_email.add_correspondents()

    assert Correspondent.objects.count() == 1
    assert fake_email.correspondents.count() == 1
    assert (
        fake_email.emailcorrespondents.filter(mention=fake_mention)
        .get()
        .correspondent.email_address
        == fake_email_address
    )


@pytest.mark.django_db
def test_Email_add_correspondents_multi(faker, fake_email):
    fake_email_address_1 = faker.email()
    fake_email_address_2 = faker.email()
    fake_mention_1 = faker.random_element(HeaderFields.Correspondents.values)
    fake_mention_2 = faker.random_element(HeaderFields.Correspondents.values)
    fake_mentioned_correspondent_1 = baker.make(
        Correspondent,
        email_address=fake_email_address_1,
        user=fake_email.mailbox.account.user,
    )
    fake_mentioned_correspondent_2 = baker.make(
        Correspondent,
        email_address=fake_email_address_2,
        user=fake_email.mailbox.account.user,
    )
    fake_email.headers = {
        fake_mention_1: fake_email_address_1,
        fake_mention_2: "  " + fake_email_address_2 + " ",
    }

    assert fake_email.correspondents.count() == 0

    fake_email.add_correspondents()

    assert fake_email.correspondents.count() == 2
    assert fake_mentioned_correspondent_1 in fake_email.correspondents.all()
    assert fake_mentioned_correspondent_2 in fake_email.correspondents.all()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_email_path, expected_email_features, expected_correspondents_features,expected_attachments_features",
    TEST_EMAIL_PARAMETERS,
)
def test_Email_create_from_email_bytes_success(
    override_config,
    fake_mailbox,
    mock_logger,
    mock_Email_save_eml_to_storage,
    mock_Attachment_save_to_storage,
    test_email_path,
    expected_email_features,
    expected_correspondents_features,
    expected_attachments_features,
):
    """Tests :func:`core.models.Email.Email.create_from_email_bytes`
    in case of success.
    """
    with open(test_email_path, "br") as test_email_file:
        test_email_bytes = test_email_file.read()

    with override_config(THROW_OUT_SPAM=False):
        result = Email.create_from_email_bytes(test_email_bytes, mailbox=fake_mailbox)

    assert isinstance(result, Email)
    assert result.pk is not None
    assert result.message_id == expected_email_features["message_id"]
    assert result.email_subject == expected_email_features["email_subject"]
    assert result.x_spam == expected_email_features["x_spam"]
    assert result.plain_bodytext == expected_email_features["plain_bodytext"]
    assert result.html_bodytext == expected_email_features["html_bodytext"]
    assert result.attachments.count() == len(expected_attachments_features)
    for item in result.attachments.all():
        assert item.file_name in expected_attachments_features
        assert (
            item.content_disposition
            == expected_attachments_features[item.file_name]["content_disposition"]
        )
        assert (
            item.content_maintype
            == expected_attachments_features[item.file_name]["content_maintype"]
        )
        assert (
            item.content_subtype
            == expected_attachments_features[item.file_name]["content_subtype"]
        )
        assert (
            item.content_id
            == expected_attachments_features[item.file_name]["content_id"]
        )
    assert result.emailcorrespondents.count() == sum(
        [
            len(correspondents)
            for correspondents in expected_correspondents_features.values()
        ]
    )
    for item in result.emailcorrespondents.all():
        assert item.mention in expected_correspondents_features
        assert (
            item.correspondent.email_address
            in expected_correspondents_features[item.mention]
        )
    assert len(result.headers) == expected_email_features["header_count"]
    assert result.mailbox == fake_mailbox
    if expected_attachments_features:
        mock_Attachment_save_to_storage.assert_called()
    mock_Email_save_eml_to_storage.assert_called()
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()
    mock_logger.critical.assert_not_called()


@pytest.mark.django_db
def test_Email_create_from_email_bytes_duplicate(
    override_config,
    fake_email,
    mock_logger,
    mock_Email_save_eml_to_storage,
    mock_Attachment_save_to_storage,
):
    """Tests :func:`core.models.Email.Email.create_from_email_bytes`
    in case the email to be parsed is already in the database.
    """
    with override_config(THROW_OUT_SPAM=False):
        result = Email.create_from_email_bytes(
            f"Message-ID: {fake_email.message_id}".encode(), fake_email.mailbox
        )

    assert result is None
    mock_Attachment_save_to_storage.assert_not_called()
    mock_Email_save_eml_to_storage.assert_not_called()
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()
    mock_logger.exception.assert_not_called()
    mock_logger.critical.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "X_Spam_Flag, THROW_OUT_SPAM, expected_is_none",
    [
        ("YES", True, True),
        ("NO", True, False),
        ("YES, NO", True, True),
        ("NO, YES", True, True),
        ("NO, NO", True, False),
        ("SOMETHING", True, False),
        ("YES", False, False),
        ("NO", False, False),
        ("YES, NO", False, False),
        ("NO, YES", False, False),
        ("NO, NO", False, False),
        ("SOMETHING", False, False),
    ],
)
def test_Email_create_from_email_bytes_spam(
    override_config,
    fake_mailbox,
    mock_logger,
    mock_Email_save_eml_to_storage,
    mock_Attachment_save_to_storage,
    X_Spam_Flag,
    THROW_OUT_SPAM,
    expected_is_none,
):
    """Tests :func:`core.models.Email.Email.create_from_email_bytes`
    with regard to spam emails.
    """
    with override_config(THROW_OUT_SPAM=THROW_OUT_SPAM):
        result = Email.create_from_email_bytes(
            f"X-Spam-Flag: {X_Spam_Flag}".encode(), fake_mailbox
        )

    assert (result is None) is expected_is_none
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()
    mock_logger.exception.assert_not_called()
    mock_logger.critical.assert_not_called()


@pytest.mark.django_db
def test_Email_create_from_email_bytes_dberror(
    mocker, override_config, fake_mailbox, mock_logger
):
    """Tests :func:`core.models.Email.Email.create_from_email_bytes`
    in case an database :class:`django.db.IntegrityError` occurs.
    """
    mock_Email_save = mocker.patch(
        "core.models.Email.Email.save",
        autospec=True,
        side_effect=IntegrityError,
    )

    with override_config(THROW_OUT_SPAM=False):
        result = Email.create_from_email_bytes(b"Message-ID: something", fake_mailbox)

    assert result is None
    mock_Email_save.assert_called()
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.exception.assert_called()
    mock_logger.critical.assert_not_called()


@pytest.mark.django_db
def test_Email_html_version(fake_email, fake_attachment, fake_correspondent):
    result = fake_email.html_version

    assert result
    assert get_config("EMAIL_CSS") in result


@pytest.mark.django_db
@pytest.mark.parametrize(
    "eml_filepath, expected_has_download",
    [
        (None, False),
        ("some/file/path", True),
    ],
)
def test_Email_has_download(fake_email, eml_filepath, expected_has_download):
    """Tests :func:`core.models.Email.Email.has_download` in the two relevant cases."""
    fake_email.eml_filepath = eml_filepath

    result = fake_email.has_download

    assert result == expected_has_download


@pytest.mark.django_db
@pytest.mark.parametrize(
    "x_spam, expected_has_download",
    [
        ("NO", True),
        ("NO, NO", True),
        ("YES", False),
        ("YES,NO", False),
        ("", True),
    ],
)
def test_Email_has_thumbnail(fake_email, x_spam, expected_has_download):
    """Tests :func:`core.models.Email.Email.has_download` in the two relevant cases."""
    fake_email.x_spam = x_spam

    result = fake_email.has_thumbnail

    assert result == expected_has_download


@pytest.mark.django_db
def test_Email_has_thumbnail_with_file(fake_email_with_file):
    """Tests :func:`core.models.Email.Email.has_download` for an email with files."""
    result = fake_email_with_file.has_thumbnail

    assert result is True


@pytest.mark.django_db
def test_Email_has_thumbnail_no_file(fake_email):
    """Tests :func:`core.models.Email.Email.has_download` for an email without files."""
    result = fake_email.has_thumbnail

    assert result is True


@pytest.mark.django_db
def test_Email_get_absolute_thumbnail_url(fake_email):
    """Tests :func:`core.models.Email.Email.get_absolute_thumbnail_url`."""
    result = fake_email.get_absolute_thumbnail_url()

    assert result == reverse(
        f"api:v1:{fake_email.BASENAME}-thumbnail", kwargs={"pk": fake_email.pk}
    )


@pytest.mark.django_db
def test_Email_get_absolute_url(fake_email):
    """Tests :func:`core.models.Email.Email.get_absolute_url`."""
    result = fake_email.get_absolute_url()

    assert result == reverse(
        f"web:{fake_email.BASENAME}-detail", kwargs={"pk": fake_email.pk}
    )


@pytest.mark.django_db
def test_Email_get_absolute_list_url(fake_email):
    """Tests :func:`core.models.Email.Email.get_absolute_list_url`."""
    result = fake_email.get_absolute_list_url()

    assert result == reverse(
        f"web:{fake_email.BASENAME}-filter-list",
    )
