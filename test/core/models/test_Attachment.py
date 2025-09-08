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

"""Test module for :mod:`core.models.Attachment`."""

import datetime
import email
import os
from tempfile import gettempdir
from zipfile import ZipFile

import httpx
import pytest
from django.core.files.storage import default_storage
from django.db import IntegrityError
from django.urls import reverse
from model_bakery import baker
from pyfakefs.fake_filesystem_unittest import Pause

from core.models import Attachment, Email
from test.conftest import TEST_EMAIL_PARAMETERS


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    """Fixture mocking the logger :attr:`core.models.Attachment.logger` of the module."""
    return mocker.patch("core.models.Attachment.logger", autospec=True)


@pytest.fixture
def mock_httpx_post(mocker, faker):
    """Fixture mocking the post method of :mod:`httpx`."""
    fake_response = httpx.Response(
        200,
        content=f'{{"{faker.word()}": "{faker.uuid4()}"}}',
        request=httpx.Request("post", faker.url()),
    )
    return mocker.patch("httpx.post", autospec=True, return_value=fake_response)


@pytest.mark.django_db
def test_Attachment_fields(fake_attachment):
    """Tests the fields of :class:`core.models.Attachment.Attachment`."""

    assert fake_attachment.file_name is not None
    assert isinstance(fake_attachment.file_name, str)
    assert fake_attachment.file_path is None
    assert fake_attachment.datasize is not None
    assert isinstance(fake_attachment.datasize, int)
    assert fake_attachment.is_favorite is False
    assert fake_attachment.email is not None
    assert isinstance(fake_attachment.email, Email)
    assert fake_attachment.updated is not None
    assert isinstance(fake_attachment.updated, datetime.datetime)
    assert fake_attachment.created is not None
    assert isinstance(fake_attachment.created, datetime.datetime)


@pytest.mark.django_db
def test_Attachment___str__(fake_attachment):
    """Tests the string representation of :class:`core.models.Attachment.Attachment`."""
    assert fake_attachment.file_name in str(fake_attachment)
    assert str(fake_attachment.email) in str(fake_attachment)


@pytest.mark.django_db
def test_Attachment_foreign_key_deletion(fake_attachment):
    """Tests the on_delete foreign key constraint in :class:`core.models.Attachment.Attachment`."""

    assert fake_attachment is not None
    fake_attachment.email.delete()
    with pytest.raises(Attachment.DoesNotExist):
        fake_attachment.refresh_from_db()


@pytest.mark.django_db
def test_Attachment_unique_constraints():
    """Tests the unique constraints of :class:`core.models.Attachment.Attachment`."""
    email = baker.make(Email, x_spam="NO")

    baker.make(Attachment, file_path="test", email=email)
    with pytest.raises(IntegrityError):
        baker.make(Attachment, file_path="test", email=email)


@pytest.mark.django_db
def test_Attachment_delete_attachmentfile_success(
    fake_attachment_with_file,
    mock_logger,
):
    """Tests :func:`core.models.Attachment.Attachment.delete`
    in case the file removal is successful.
    """
    previous_file_path = fake_attachment_with_file.file_path

    fake_attachment_with_file.delete()

    with pytest.raises(Attachment.DoesNotExist):
        fake_attachment_with_file.refresh_from_db()
    assert not default_storage.exists(previous_file_path)


@pytest.mark.django_db
def test_Attachment_delete_attachmentfile_delete_error(
    mocker,
    fake_attachment_with_file,
    mock_logger,
):
    """Tests :func:`core.models.Attachment.Attachment.delete`
    in case delete raises an exception.
    """
    mock_delete = mocker.patch(
        "core.models.Attachment.models.Model.delete",
        autospec=True,
        side_effect=AssertionError,
    )

    with pytest.raises(AssertionError):
        fake_attachment_with_file.delete()

    assert default_storage.exists(fake_attachment_with_file.file_path)
    mock_delete.assert_called_once()
    mock_logger.debug.assert_not_called()


@pytest.mark.django_db
def test_Attachment_save_with_data(
    fake_fs,
    fake_email,
    fake_file_bytes,
):
    """Tests :func:`core.models.Attachment.Attachment.save`
    in case of success with data to be saved.
    """
    new_attachment = baker.make(Attachment, email=fake_email)

    assert fake_email.mailbox.save_to_eml is True
    assert new_attachment.file_path is None

    new_attachment.save(file_payload=fake_file_bytes)

    new_attachment.refresh_from_db()
    assert new_attachment.pk
    assert new_attachment.file_path is not None
    assert (
        os.path.basename(new_attachment.file_path)
        == str(new_attachment.pk) + "_" + new_attachment.file_name
    )
    assert default_storage.open(new_attachment.file_path).read() == fake_file_bytes


@pytest.mark.django_db
def test_Attachment_save_with_data_no_save_attachments(
    fake_fs,
    fake_email,
    fake_file_bytes,
):
    """Tests :func:`core.models.Attachment.Attachment.save`
    in case of success with data to be saved and `save_to_eml` set to False.
    """
    fake_email.mailbox.save_attachments = False
    fake_email.mailbox.save(update_fields=["save_attachments"])
    new_attachment = baker.make(Attachment, email=fake_email)

    assert new_attachment.file_path is None

    new_attachment.save(file_payload=fake_file_bytes)

    new_attachment.refresh_from_db()
    assert new_attachment.pk
    assert new_attachment.file_path is None


@pytest.mark.django_db
def test_Attachment_save_with_data_file_path_set(
    faker,
    fake_email,
    fake_file_bytes,
):
    """Tests :func:`core.models.Attachment.Attachment.save`
    in case of success with data to be saved and `save_to_eml` set to False.
    """
    fake_file_name = faker.file_name()
    new_attachment = baker.make(Attachment, email=fake_email, file_path=fake_file_name)

    assert fake_email.mailbox.save_attachments is True
    assert new_attachment.file_path == fake_file_name

    new_attachment.save(file_payload=fake_file_bytes)

    new_attachment.refresh_from_db()
    assert new_attachment.pk
    assert new_attachment.file_path == fake_file_name


@pytest.mark.django_db
def test_Attachment_save_no_data_success(
    fake_email,
):
    """Tests :func:`core.models.Attachment.Attachment.save`
    in case of success with data to be saved.
    """
    new_attachment = baker.make(Attachment, email=fake_email)

    assert fake_email.mailbox.save_attachments is True
    assert new_attachment.file_path is None

    new_attachment.save()

    new_attachment.refresh_from_db()
    assert new_attachment.pk
    assert new_attachment.file_path is None


def test_Attachment_open_file_success(fake_attachment_with_file):
    """Tests :func:`core.models.Attachment.Attachment.open_file`
    in case of success.
    """
    result = fake_attachment_with_file.open_file()

    with default_storage.open(
        fake_attachment_with_file.file_path, "rb"
    ) as attachment_file:
        assert result.read() == attachment_file.read()

    result.close()


def test_Attachment_open_file_no_filepath(fake_attachment_with_file):
    """Tests :func:`core.models.Attachment.Attachment.open_file`
    in case the filepath on the instance is not set.
    """
    fake_attachment_with_file.file_path = None

    with pytest.raises(FileNotFoundError), fake_attachment_with_file.open_file():
        pass


def test_Attachment_open_file_no_file(faker, fake_attachment):
    """Tests :func:`core.models.Attachment.Attachment.open_file`
    in case the file can't be found in the storage.
    """
    fake_attachment.file_path = faker.file_name()

    with pytest.raises(FileNotFoundError), fake_attachment.open_file():
        pass


@pytest.mark.django_db
@pytest.mark.parametrize(
    "maintype, subtype, expected_mimetype",
    [
        ("abc", "xyz", "abc/xyz"),
        ("tyu", "", ""),
        ("", "gh4", ""),
        ("", "", ""),
    ],
)
def test_Attachment_content_type(fake_attachment, maintype, subtype, expected_mimetype):
    """Tests :func:`core.models.Attachment.Attachment.content_type`
    for different cases of main- subtype combinations.
    """
    fake_attachment.content_maintype = maintype
    fake_attachment.content_subtype = subtype

    result = fake_attachment.content_type

    assert result == expected_mimetype


@pytest.mark.django_db
def test_Attachment_queryset_as_file(
    fake_file, fake_attachment, fake_attachment_with_file
):
    """Tests :func:`core.models.Attachment.Attachment.queryset_as_file`
    in case of success.
    """
    assert Attachment.objects.count() == 2

    result = Attachment.queryset_as_file(Attachment.objects.all())

    assert Attachment.objects.count() == 2
    assert hasattr(result, "read")
    with ZipFile(result) as zipfile:
        assert zipfile.namelist() == [
            os.path.basename(fake_attachment_with_file.file_path)
        ]
        with zipfile.open(
            os.path.basename(fake_attachment_with_file.file_path)
        ) as zipped_file:
            assert zipped_file.read().strip() == fake_file.getvalue().strip()
    assert hasattr(result, "close")
    result.close()
    assert os.listdir(gettempdir()) == []


@pytest.mark.django_db
def test_Attachment_queryset_as_file_empty_queryset():
    """Tests :func:`core.models.Attachment.Attachment.queryset_as_file`
    in case the queryset is empty.
    """
    assert Attachment.objects.count() == 0

    with pytest.raises(Attachment.DoesNotExist):
        Attachment.queryset_as_file(Attachment.objects.none())

    assert Attachment.objects.count() == 0


@pytest.mark.django_db
def test_Attachment_share_to_paperless_success(
    faker, fake_attachment_with_file, mock_logger, mock_httpx_post
):
    """Tests :func:`core.models.Attachment.Attachment.share_to_paperless`
    in case of success.
    """
    profile = fake_attachment_with_file.email.mailbox.account.user.profile
    profile.paperless_url = faker.url()
    profile.paperless_api_key = faker.word()
    profile.save()

    result = fake_attachment_with_file.share_to_paperless()

    assert result == mock_httpx_post.return_value.json()
    mock_httpx_post.assert_called_once()
    assert (
        mock_httpx_post.call_args.args[0]
        == profile.paperless_url.strip("/") + "/api/documents/post_document/"
    )
    assert mock_httpx_post.call_args.kwargs["data"] == {
        "title": fake_attachment_with_file.file_name,
        "created": str(fake_attachment_with_file.created),
    }
    assert mock_httpx_post.call_args.kwargs["headers"] == {
        "Authorization": f"Token {profile.paperless_api_key}"
    }
    assert (
        mock_httpx_post.call_args.kwargs["files"]["document"][0]
        == fake_attachment_with_file.file_name
    )
    assert mock_httpx_post.call_args.kwargs["files"]["document"][
        1
    ].name == default_storage.path(fake_attachment_with_file.file_path)
    assert (
        mock_httpx_post.call_args.kwargs["files"]["document"][2]
        == fake_attachment_with_file.content_type
    )
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_Attachment_share_to_paperless_no_file(fake_attachment):
    """Tests :func:`core.models.Attachment.Attachment.share_to_paperless`
    in case the attachment has no file.
    """
    with pytest.raises(FileNotFoundError):
        fake_attachment.share_to_paperless()


@pytest.mark.django_db
def test_Attachment_share_to_paperless_no_api_key(
    faker, fake_attachment_with_file, mock_logger, mock_httpx_post
):
    """Tests :func:`core.models.Attachment.Attachment.share_to_paperless`
    in case there is no apikey.
    This test makes sure there is no error constructing the header.
    """
    fake_attachment_with_file.email.mailbox.account.user.profile.paperless_url = (
        faker.url()
    )
    fake_attachment_with_file.email.mailbox.account.user.profile.save()
    mock_httpx_post.return_value.status_code = 401

    with pytest.raises(PermissionError):
        fake_attachment_with_file.share_to_paperless()

    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize("paperless_url", ["test.org", "smb://100.200.051.421", ""])
def test_Attachment_share_to_paperless_error_request_setup(
    fake_attachment_with_file, mock_logger, paperless_url
):
    """Tests :func:`core.models.Attachment.Attachment.share_to_paperless`
    in case of an error with the request.
    """
    fake_attachment_with_file.email.mailbox.account.user.profile.paperless_url = (
        paperless_url
    )
    fake_attachment_with_file.email.mailbox.account.user.profile.save()

    with pytest.raises(RuntimeError):
        fake_attachment_with_file.share_to_paperless()

    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_Attachment_share_to_paperless_error_request(
    fake_error_message,
    fake_attachment_with_file,
    mock_logger,
    mock_httpx_post,
):
    """Tests :func:`core.models.Attachment.Attachment.share_to_paperless`
    in case of an error with the request.
    """
    mock_httpx_post.side_effect = httpx.RequestError(fake_error_message)

    with pytest.raises(ConnectionError, match=fake_error_message):
        fake_attachment_with_file.share_to_paperless()

    mock_httpx_post.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize("status_code", [401, 403])
def test_Attachment_share_to_paperless_unauthorized(
    fake_error_message,
    fake_attachment_with_file,
    mock_httpx_post,
    mock_logger,
    status_code,
):
    """Tests :func:`core.models.Attachment.Attachment.share_to_paperless`
    in case of an error authenticating.
    """
    mock_httpx_post.return_value = httpx.Response(
        status_code,
        content=f'{{"detail": "{fake_error_message}"}}',
        request=mock_httpx_post.return_value.request,
    )

    with pytest.raises(PermissionError, match=fake_error_message):
        fake_attachment_with_file.share_to_paperless()

    mock_httpx_post.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize("status_code", [400, 500, 300])
def test_Attachment_share_to_paperless_error_status(
    fake_error_message,
    fake_attachment_with_file,
    mock_httpx_post,
    mock_logger,
    status_code,
):
    """Tests :func:`core.models.Attachment.Attachment.share_to_paperless`
    in case of a bad status response.
    """
    mock_httpx_post.return_value = httpx.Response(
        status_code,
        content=f'{{"detail": "{fake_error_message}"}}',
        request=mock_httpx_post.return_value.request,
    )

    with pytest.raises(ValueError, match=fake_error_message):
        fake_attachment_with_file.share_to_paperless()

    mock_httpx_post.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_email_path, expected_email_features, expected_correspondents_features,expected_attachments_features",
    TEST_EMAIL_PARAMETERS,
)
def test_Attachment_from_data(
    fake_fs,
    fake_email,
    test_email_path,
    expected_email_features,
    expected_correspondents_features,
    expected_attachments_features,
):
    """Tests :func:`core.models.Attachment.Attachment.from_data`
    in case of success.
    """
    with Pause(fake_fs), open(test_email_path, "br") as test_email_file:
        test_email_bytes = test_email_file.read()
    test_email_message = email.message_from_bytes(test_email_bytes)

    result = Attachment.create_from_email_message(test_email_message, fake_email)

    assert isinstance(result, list)
    assert all(isinstance(item, Attachment) for item in result)
    assert len(result) == len(expected_attachments_features)
    for item in result:
        assert item.pk is not None
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
        assert item.file_path is not None


@pytest.mark.django_db
@pytest.mark.parametrize(
    "file_path, expected_has_download",
    [
        (None, False),
        ("some/file/path", True),
    ],
)
def test_Attachment_has_download(fake_attachment, file_path, expected_has_download):
    """Tests :func:`core.models.Attachment.Attachment.has_download` in the two relevant cases."""
    fake_attachment.file_path = file_path

    result = fake_attachment.has_download

    assert result == expected_has_download


@pytest.mark.django_db
@pytest.mark.parametrize(
    "content_maintype, content_subtype, expected_has_thumbnail",
    [
        ("", "", False),
        ("oo4vuy0s9yn", "a4ueiofdsj", False),
        ("image", "734reoj", True),
        ("font", "asdfr", True),
        ("video", "mp4", True),
        ("video", "45rtyghj", False),
        ("text", "html", True),
        ("text", "8549c", True),
        ("text", "calendar", False),
        ("application", "pdf", True),
        ("application", "json", True),
        ("application", "xml", True),
        ("application", "rss+xml", True),
        ("application", "javascript", True),
        ("application", "emnoscript", True),
        ("application", "854uqw", False),
    ],
)
def test_Attachment_has_thumbnail_with_file(
    fake_attachment_with_file, content_maintype, content_subtype, expected_has_thumbnail
):
    """Tests :func:`core.models.Attachment.Attachment.has_thumbnail` in the two relevant cases."""
    fake_attachment_with_file.content_maintype = content_maintype
    fake_attachment_with_file.content_subtype = content_subtype
    fake_attachment_with_file.datasize = 0

    result = fake_attachment_with_file.has_thumbnail

    assert result == expected_has_thumbnail


@pytest.mark.django_db
@pytest.mark.parametrize(
    "content_maintype, content_subtype",
    [
        ("image", "734reoj"),
        ("font", "asdfr"),
        ("video", "mp4"),
        ("video", "45rtyghj"),
        ("text", "html"),
        ("text", "8549c"),
        ("text", "calendar"),
        ("application", "pdf"),
        ("application", "json"),
        ("application", "xml"),
        ("application", "rss+xml"),
        ("application", "javascript"),
        ("application", "emnoscript"),
        ("application", "854uqw"),
    ],
)
def test_Attachment_has_thumbnail_no_file(
    fake_attachment, content_maintype, content_subtype
):
    """Tests :func:`core.models.Attachment.Attachment.has_thumbnail` in the two relevant cases."""
    fake_attachment.content_maintype = content_maintype
    fake_attachment.content_subtype = content_subtype

    result = fake_attachment.has_thumbnail

    assert result is False


@pytest.mark.django_db
@pytest.mark.parametrize(
    "content_maintype, content_subtype",
    [
        ("image", "734reoj"),
        ("font", "asdfr"),
        ("video", "mp4"),
        ("video", "45rtyghj"),
        ("text", "html"),
        ("text", "8549c"),
        ("text", "calendar"),
        ("application", "pdf"),
        ("application", "json"),
        ("application", "xml"),
        ("application", "rss+xml"),
        ("application", "javascript"),
        ("application", "emnoscript"),
        ("application", "854uqw"),
    ],
)
def test_Attachment_has_thumbnail_spam(
    fake_attachment_with_file, content_maintype, content_subtype
):
    """Tests :func:`core.models.Attachment.Attachment.has_thumbnail` in the two relevant cases."""
    fake_attachment_with_file.content_maintype = content_maintype
    fake_attachment_with_file.content_subtype = content_subtype
    fake_attachment_with_file.datasize = 0
    fake_attachment_with_file.email.x_spam = "YES"
    fake_attachment_with_file.email.save()

    result = fake_attachment_with_file.has_thumbnail

    assert result is False


@pytest.mark.django_db
@pytest.mark.parametrize(
    "content_maintype, content_subtype",
    [
        ("image", "734reoj"),
        ("font", "asdfr"),
        ("video", "mp4"),
        ("video", "45rtyghj"),
        ("text", "html"),
        ("text", "8549c"),
        ("text", "calendar"),
        ("application", "pdf"),
        ("application", "json"),
        ("application", "xml"),
        ("application", "rss+xml"),
        ("application", "javascript"),
        ("application", "emnoscript"),
        ("application", "854uqw"),
    ],
)
def test_Attachment_has_thumbnail_too_large(
    override_config, fake_attachment, content_maintype, content_subtype
):
    """Tests :func:`core.models.Attachment.Attachment.has_thumbnail` in the two relevant cases."""
    fake_attachment.content_maintype = content_maintype
    fake_attachment.content_subtype = content_subtype

    with override_config(WEB_THUMBNAIL_MAX_DATASIZE=0):
        result = fake_attachment.has_thumbnail

    assert result is False


@pytest.mark.django_db
@pytest.mark.parametrize(
    "content_maintype, content_subtype, expected_is_shareable_to_paperless",
    [
        ("", "", False),
        ("oo4vuy0s9yn", "a4ueiofdsj", False),
        ("image", "jpeg", True),
        ("image", "pjpeg", True),
        ("image", "png", True),
        ("image", "tiff", True),
        ("image", "x-tiff", True),
        ("image", "gif", True),
        ("image", "raw", False),
        ("text", "plain", True),
        ("text", "html", False),
        ("font", "woff", False),
        ("application", "pdf", True),
        ("application", "json", False),
        ("application", "msword", False),
        (
            "application",
            "vnd.openxmlformats-officedocument.wordprocessingml.document",
            False,
        ),
        ("application", "vnd.oasis.opendocument.text", False),
        ("application", "powerpoint", False),
        ("application", "mspowerpoint", False),
        ("application", "vnd.ms-powerpoint", False),
        (
            "application",
            "vnd.openxmlformats-officedocument.presentationml.presentation",
            False,
        ),
        ("application", "vnd.oasis.opendocument.presentation", False),
        ("application", "excel", False),
        ("application", "msexcel", False),
        ("application", "x-excel", False),
        ("application", "x-msexcel", False),
        ("application", "vnd.ms-excel", False),
        ("application", "vnd.openxmlformats-officedocument.spreadsheetml.sheet", False),
        ("application", "vnd.oasis.opendocument.spreadsheet", False),
    ],
)
def test_Attachment_is_shareable_to_paperless_with_file_no_tika(
    fake_attachment_with_file,
    content_maintype,
    content_subtype,
    expected_is_shareable_to_paperless,
):
    """Tests :func:`core.models.Attachment.Attachment.is_shareable_to_paperless` in the two relevant cases."""
    fake_attachment_with_file.content_maintype = content_maintype
    fake_attachment_with_file.content_subtype = content_subtype
    fake_attachment_with_file.email.mailbox.account.user.profile.paperless_tika_enabled = (
        False
    )
    fake_attachment_with_file.email.mailbox.account.user.profile.save()

    result = fake_attachment_with_file.is_shareable_to_paperless

    assert result == expected_is_shareable_to_paperless


@pytest.mark.django_db
@pytest.mark.parametrize(
    "content_maintype, content_subtype, expected_is_shareable_to_paperless",
    [
        ("", "", False),
        ("oo4vuy0s9yn", "a4ueiofdsj", False),
        ("image", "jpeg", True),
        ("image", "pjpeg", True),
        ("image", "png", True),
        ("image", "tiff", True),
        ("image", "x-tiff", True),
        ("image", "gif", True),
        ("image", "raw", False),
        ("text", "plain", True),
        ("text", "html", False),
        ("font", "woff", False),
        ("application", "pdf", True),
        ("application", "json", False),
        ("application", "msword", True),
        (
            "application",
            "vnd.openxmlformats-officedocument.wordprocessingml.document",
            True,
        ),
        ("application", "vnd.oasis.opendocument.text", True),
        ("application", "powerpoint", True),
        ("application", "mspowerpoint", True),
        ("application", "vnd.ms-powerpoint", True),
        (
            "application",
            "vnd.openxmlformats-officedocument.presentationml.presentation",
            True,
        ),
        ("application", "vnd.oasis.opendocument.presentation", True),
        ("application", "excel", True),
        ("application", "msexcel", True),
        ("application", "x-excel", True),
        ("application", "x-msexcel", True),
        ("application", "vnd.ms-excel", True),
        ("application", "vnd.openxmlformats-officedocument.spreadsheetml.sheet", True),
        ("application", "vnd.oasis.opendocument.spreadsheet", True),
    ],
)
def test_Attachment_is_shareable_to_paperless_with_file_with_tika(
    fake_attachment_with_file,
    content_maintype,
    content_subtype,
    expected_is_shareable_to_paperless,
):
    """Tests :func:`core.models.Attachment.Attachment.is_shareable_to_paperless` in the two relevant cases."""
    fake_attachment_with_file.content_maintype = content_maintype
    fake_attachment_with_file.content_subtype = content_subtype
    fake_attachment_with_file.email.mailbox.account.user.profile.paperless_tika_enabled = (
        True
    )
    fake_attachment_with_file.email.mailbox.account.user.profile.save()

    result = fake_attachment_with_file.is_shareable_to_paperless

    assert result == expected_is_shareable_to_paperless


@pytest.mark.django_db
@pytest.mark.parametrize(
    "content_maintype, content_subtype",
    [
        ("", ""),
        ("oo4vuy0s9yn", "a4ueiofdsj"),
        ("image", "jpeg"),
        ("image", "pjpeg"),
        ("image", "png"),
        ("image", "tiff"),
        ("image", "x-tiff"),
        ("image", "gif"),
        ("image", "raw"),
        ("text", "plain"),
        ("text", "html"),
        ("font", "woff"),
        ("application", "pdf"),
        ("application", "json"),
        ("application", "msword"),
        (
            "application",
            "vnd.openxmlformats-officedocument.wordprocessingml.document",
        ),
        ("application", "vnd.oasis.opendocument.text"),
        ("application", "powerpoint"),
        ("application", "mspowerpoint"),
        ("application", "vnd.ms-powerpoint"),
        (
            "application",
            "vnd.openxmlformats-officedocument.presentationml.presentation",
        ),
        ("application", "vnd.oasis.opendocument.presentation"),
        ("application", "excel"),
        ("application", "msexcel"),
        ("application", "x-excel"),
        ("application", "x-msexcel"),
        ("application", "vnd.ms-excel"),
        ("application", "vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        ("application", "vnd.oasis.opendocument.spreadsheet"),
    ],
)
def test_Attachment_is_shareable_to_paperless_no_file(
    fake_attachment, content_maintype, content_subtype
):
    """Tests :func:`core.models.Attachment.Attachment.is_shareable_to_paperless` in the two relevant cases."""
    fake_attachment.content_maintype = content_maintype
    fake_attachment.content_subtype = content_subtype

    result = fake_attachment.is_shareable_to_paperless

    assert result is False


@pytest.mark.django_db
def test_Attachment_get_absolute_thumbnail_url(fake_attachment):
    """Tests :func:`core.models.Attachment.Attachment.get_absolute_thumbnail_url`."""
    result = fake_attachment.get_absolute_thumbnail_url()

    assert result == reverse(
        f"api:v1:{fake_attachment.BASENAME}-thumbnail",
        kwargs={"pk": fake_attachment.pk},
    )


@pytest.mark.django_db
def test_Attachment_get_absolute_url(fake_attachment):
    """Tests :func:`core.models.Attachment.Attachment.get_absolute_url`."""
    result = fake_attachment.get_absolute_url()

    assert result == reverse(
        f"web:{fake_attachment.BASENAME}-detail",
        kwargs={"pk": fake_attachment.pk},
    )


@pytest.mark.django_db
def test_Attachment_get_absolute_list_url(fake_attachment):
    """Tests :func:`core.models.Attachment.Attachment.get_absolute_list_url`."""
    result = fake_attachment.get_absolute_list_url()

    assert result == reverse(f"web:{fake_attachment.BASENAME}-filter-list")
