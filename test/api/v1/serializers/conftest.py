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

"""File with fixtures required for all viewset tests. Automatically imported to test_ files.

The serilalizer tests are made against a mocked consistent database with an instance of every model in every testcase.

Fixtures:
    :func:`complete_database`: Autouse all models for the tests.
"""

from __future__ import annotations

import pytest
from model_bakery import baker
from rest_framework.request import Request

from core.constants import HeaderFields
from core.models.AccountModel import AccountModel
from core.models.AttachmentModel import AttachmentModel
from core.models.CorrespondentModel import CorrespondentModel
from core.models.DaemonModel import DaemonModel
from core.models.EMailCorrespondentsModel import EMailCorrespondentsModel
from core.models.EMailModel import EMailModel
from core.models.MailboxModel import MailboxModel
from core.models.MailingListModel import MailingListModel


@pytest.fixture(autouse=True)
def request_context(mocker, owner_user):
    mock_request = mocker.MagicMock(spec=Request)
    mock_request.user = owner_user
    return {"request": mock_request}


@pytest.fixture(autouse=True)
def complete_database(
    faker,
    owner_user,
    other_user,
    accountModel,
    attachmentModel,
    correspondentModel,
    daemonModel,
    emailModel,
    mailboxModel,
    mailingListModel,
):
    other_accountModel = baker.make(AccountModel, user=other_user)
    other_mailboxModel = baker.make(MailboxModel, account=other_accountModel)
    baker.make(
        DaemonModel,
        log_filepath=faker.file_path(extension="log"),
        mailbox=other_mailboxModel,
    )
    other_emailModel = baker.make(
        EMailModel,
        mailbox=other_mailboxModel,
        mailinglist=mailingListModel,
        eml_filepath=faker.file_path(extension="eml"),
        prerender_filepath=faker.file_path(extension="png"),
    )
    baker.make(
        EMailCorrespondentsModel,
        email=other_emailModel,
        correspondent=correspondentModel,
        mention=HeaderFields.Correspondents.FROM,
    )
    baker.make(
        AttachmentModel,
        email=other_emailModel,
        file_path=faker.file_path(extension="pdf"),
    )
