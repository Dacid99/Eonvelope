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

"""Test module for the :class:`web.forms.mailbox_forms.BaseMailboxForm.BaseMailboxForm` form class."""


import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from web.forms.UploadEmailForm import UploadEmailForm


@pytest.fixture
def file_payload(faker, fake_file):
    return {
        "file": SimpleUploadedFile(
            faker.name(), fake_file.read(), content_type="text/plain"
        )
    }


@pytest.mark.parametrize(
    "file_format",
    [
        "eml",
        "mbox",
        "babyl",
        "mh",
        "maildir",
        "mmdf",
    ],
)
def test_post_success(file_payload, file_format):
    form = UploadEmailForm(data={"file_format": file_format}, files=file_payload)

    assert form.is_valid()


def test_post_bad_format(file_payload):
    form = UploadEmailForm(data={"file_format": "something"}, files=file_payload)

    assert not form.is_valid()


def test_post_bad_file():
    form = UploadEmailForm(data={"file_format": "something"}, files={})

    assert not form.is_valid()
