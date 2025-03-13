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

"""Conftest for :mod:`test.core`.

Fixtures:
    :func:`fixture_accountModel`: Creates an :class:`core.models.AccountModel.AccountModel` instance for testing.
    :func:`fixture_attachmentModel`: Creates an :class:`core.models.AttachmentModel.AttachmentModel` instance for testing.
    :func:`fixture_correspondentModel`: Creates an :class:`core.models.CorrespondentModel.CorrespondentModel` instance for testing.
    :func:`fixture_daemonModel`: Creates an :class:`core.models.DaemonModel.DaemonModel` instance for testing.
    :func:`fixture_emailModel`: Creates an :class:`core.models.EMailCorrespondentsModel.EMailCorrespondentsModel` instance for testing.
    :func:`fixture_emailCorrespondentsModel`: Creates an :class:`core.models.EMailModel.EMailModel` instance for testing.
    :func:`fixture_mailboxModel`: Creates an :class:`core.models.MailboxModel.MailboxModel` instance for testing.
    :func:`fixture_mailinglistModel`: Creates an :class:`core.models.MailingListModel.MailingListModel` instance for testing.
"""

from __future__ import annotations

from email.message import Message

import pytest
from model_bakery import baker

from core.models.AccountModel import AccountModel
from core.models.AttachmentModel import AttachmentModel
from core.models.CorrespondentModel import CorrespondentModel
from core.models.DaemonModel import DaemonModel
from core.models.EMailCorrespondentsModel import EMailCorrespondentsModel
from core.models.EMailModel import EMailModel
from core.models.MailboxModel import MailboxModel
from core.models.MailingListModel import MailingListModel


@pytest.fixture
def accountModel() -> AccountModel:
    """Creates an :class:`core.models.AccountModel.AccountModel` .

    Returns:
        The accountModel instance for testing.
    """
    return baker.make(AccountModel)


@pytest.fixture
def attachmentModel(faker) -> AttachmentModel:
    """Creates an :class:`core.models.AttachmentModel.AttachmentModel` owned by :attr:`owner_user`.

    Returns:
        The attachment instance for testing.
    """
    return baker.make(AttachmentModel, file_path=faker.file_path(extension="pdf"))


@pytest.fixture
def correspondentModel() -> CorrespondentModel:
    """Creates an :class:`core.models.CorrespondentModel.CorrespondentModel` instance for testing.

    Returns:
        The correspondentModel instance for testing.
    """
    return baker.make(CorrespondentModel)


@pytest.fixture
def daemonModel(faker) -> DaemonModel:
    """Creates an :class:`core.models.DaemonModel.DaemonModel`.

    Returns:
        The daemonModel instance for testing.
    """
    return baker.make(DaemonModel, log_filepath=faker.file_path(extension="log"))


@pytest.fixture
def emailModel() -> EMailModel:
    """Creates an :class:`core.models.EMailModel.EMailModel`.

    Returns:
        The emailModel instance for testing.
    """
    return baker.make(EMailModel)


@pytest.fixture
def emailCorrespondentModel() -> EMailCorrespondentsModel:
    """Creates an :class:`core.models.EMailModel.EMailModel` instance for testing.

    Returns:
        The emailCorrespondentModel instance for testing.
    """
    return baker.make(EMailCorrespondentsModel)


@pytest.fixture
def mailboxModel() -> MailboxModel:
    """Creates an :class:`core.models.MailboxModel.MailboxModel`.

    Returns:
        The mailboxModel instance for testing.
    """
    return baker.make(MailboxModel)


@pytest.fixture
def mailingListModel() -> MailingListModel:
    """Creates an :class:`core.models.MailboxModel.MailboxModel`.

    Returns:
        The mailingListModel instance for testing.
    """
    return baker.make(MailingListModel)


@pytest.fixture
def mock_message(mocker):
    return mocker.MagicMock(spec=Message)


TEST_EMAILS = [
    b"""X-Mozilla-Status: 0001
X-Mozilla-Status2: 00000000
Return-Path: <random@server.com>
Authentication-Results:  kundenserver.de; dkim=pass header.i=@server.com
Received: from mail-lf1-f44.google.com ([209.85.167.44]) by mx.kundenserver.de
 (mxeue102 [217.72.192.67]) with ESMTPS (Nemesis) id 1MP242-1ss5h32TGO-00IXDu
 for <the@dude.us>; Wed, 07 Aug 2024 11:41:33 +0200
Received: by mail-lf1-f44.google.com with SMTP id 2adb3069b0e04-52efc60a6e6so2449461e87.1
        for <the@dude.us>; Wed, 07 Aug 2024 02:41:33 -0700 (PDT)
DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;
        d=server.com; s=20230601; t=1723023693; x=1723628493; darn=aderbauer.org;
        h=subject:from:cc:to:user-agent:mime-version:date:message-id:from:to
         :cc:subject:date:message-id:reply-to;
        bh=RFlxTLx9fGlwRQOf0qUqe52St091bjsuM2uAJRhDBxg=;
        b=Vqnuv0OOkJaPL/3I9TBl6Dfnp/7AsGOca3m/QNFYfSMLAFgtX2eSMXPrHBwjvm8XAC
         bjbQ==
X-Google-DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;
        d=1e100.net; s=20230601; t=1723023693; x=1723628493;
        h=subject:from:cc:to:user-agent:mime-version:date:message-id
         :x-gm-message-state:from:to:cc:subject:date:message-id:reply-to;
        bh=RFlxTLx9fGlwRQOf0qUqe52St091bjsuM2uAJRhDBxg=;
        b=ZBmPe0p5DIUcFo6IofWGfBqfeGVtC/tp+ksrLH+r8C50PENNH6Yf9rglnhUaqJ7CP/
         27Wg==
X-Gm-Message-State: AOJu0YwnabjN4AiGxl+QC06gNHKmhGHxpGdywJD30comSXyvw0MF9qJL
	1BMeYDpZ+F40RM2AOnnRGCpaYjBnjGvRvBseajyMWyks2+jz2/k7Fu8uUg==
X-Google-Smtp-Source: AGHT+IG0smtMojV6Qj+RAAzDBj3MsRVttvWAmRSsioKzDuqtE3e/wiTyV76HNnTL+QjSfn+ZpvwU4w==
X-Received: by 2002:ac2:4c47:0:b0:530:ae43:d7ef with SMTP id 2adb3069b0e04-530bb39ff83mr11272803e87.48.1723023691907;
        Wed, 07 Aug 2024 02:41:31 -0700 (PDT)
Received: from [192.168.178.3] (p4ffd7c0d.dip0.t-ipconnect.de. [79.253.124.13])
        by smtp.server.com with ESMTPSA id 5b1f17b1804b1-42905796974sm21107665e9.6.2024.08.07.02.41.31
        (version=TLS1_3 cipher=TLS_AES_128_GCM_SHA256 bits=128/128);
        Wed, 07 Aug 2024 02:41:31 -0700 (PDT)
Content-Type: multipart/mixed; boundary="------------lxGwj3dPk80t53jx9NGRDA0k"
Message-ID: <e047e14d-2397-435b-baf6-8e8b7423f860@server.com>
Date: Wed, 7 Aug 2024 11:41:29 +0200
MIME-Version: 1.0
User-Agent: Mozilla Thunderbird
To: the@dude.us
Cc: cc@server.com
From: Random <random@server.com>
Subject: Whats up
Envelope-To: <the@dude.us>
X-Spam-Flag: NO
UI-InboundReport: notjunk:1;M01:P0:Mb6ajNHamrc=;jhDGG8ZKQHoVTQuDsLKZBk6yaF9m
 mFZcxlCUtKr25JfCLcbLU10=

This is a multi-part message in MIME format.
--------------lxGwj3dPk80t53jx9NGRDA0k
Content-Type: text/plain; charset=UTF-8; format=flowed
Content-Transfer-Encoding: 7bit

this a test to see how ur doin





--------------lxGwj3dPk80t53jx9NGRDA0k
Content-Type: application/json; name="manifest.json"
Content-Disposition: attachment; filename="manifest.json"
Content-Transfer-Encoding: base64

ewogICJtYW5pZmVzdF92ZXJzaW9uIjogMiwKICAibmFtZSI6ICJVbml2ZXJzYWwgSGlnaGxp
b250ZW50U2NyaXB0LmpzIl0KICAgIH0KICBdCn0KCg==

--------------lxGwj3dPk80t53jx9NGRDA0k--
""",
    b"""X-Mozilla-Status: 0001
X-Mozilla-Status2: 00000000
Return-Path: <sender@mail.com>
Authentication-Results:  kundenserver.de; dkim=pass header.i=@mail.com
Received: from mail-wm1-f44.google.com ([209.85.128.44]) by mx.kundenserver.de
 (mxeue103 [217.72.192.67]) with ESMTPS (Nemesis) id 1MsbW9-1tqYUa13Nr-00u3LP
 for <archiv@mail.org>; Sat, 05 Oct 2024 14:43:23 +0200
Received: by mail-wm1-f44.google.com with SMTP id 5b1f17b1804b1-42cde6b5094so29930975e9.3
        for <tree@mail.org>; Sat, 05 Oct 2024 05:43:23 -0700 (PDT)
DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;
        d=mail.com; s=20230601; t=1728132203; x=1728737003; darn=mail.org;
        h=subject:to:content-language:user-agent:mime-version:date:message-id
         :from:from:to:cc:subject:date:message-id:reply-to;
        bh=UR6nQj4nuqy1zwp5l1f7D3XhlsbnvU+iqqGxoxoBBj8=;
        b=la13bS9plMyYpxhNnbqwO8Wtu2DfzMx2B6yf0oOQ9X03rMqtYFlOYRZoG8XVhXwNAY
         /68g==
X-Google-DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;
        d=1e100.net; s=20230601; t=1728132203; x=1728737003;
        h=subject:to:content-language:user-agent:mime-version:date:message-id
         :from:x-gm-message-state:from:to:cc:subject:date:message-id:reply-to;
        bh=UR6nQj4nuqy1zwp5l1f7D3XhlsbnvU+iqqGxoxoBBj8=;
        b=rwHsK7dSpTDLSZCo0Ny64orbpro9BdviQKhfKQUa3wBP/Ulj27+Jk9QasR4G0ze+So
         m2Pg==
X-Gm-Message-State: AOJu0Yycfh8UhmiofMf6xk572uMF/2rSN2PEvgXc0WyCARcJszqbpEgM
	JUK2e57X3WfnSsF/qcucJvg8Q8wOOQ7liY5UrdrDoEaC80FEdc08eB8kUw==
X-Google-Smtp-Source: AGHT+IEGxdd9q9iQOIATV2wl2kIQGrex6Wtywja39cZslq95e8sTGgph0SAPHc6DEOq5Mpl8ob04PA==
X-Received: by 2002:a05:600c:468f:b0:42c:af06:718 with SMTP id 5b1f17b1804b1-42f85aea086mr44780945e9.28.1728132202401;
        Sat, 05 Oct 2024 05:43:22 -0700 (PDT)
Received: from [192.168.178.101] (p4ffd704e.dip0.t-ipconnect.de. [79.253.112.78])
        by smtp.mail.com with ESMTPSA id 5b1f17b1804b1-42f86a20471sm39424645e9.17.2024.10.05.05.43.21
        for <archiv@mail.org>
        (version=TLS1_3 cipher=TLS_AES_128_GCM_SHA256 bits=128/128);
        Sat, 05 Oct 2024 05:43:21 -0700 (PDT)
From: Sender <sender@mail.com>
X-Google-Original-From: Sender <sender@mail.com>
Content-Type: multipart/alternative;
 boundary="------------40Tk0emvCICBGcRiucnjKbPe"
Message-ID: <a634b121-4bc0-457d-a08f-a4579b9bb92a@mail.com>
Date: Sat, 5 Oct 2024 14:43:21 +0200
MIME-Version: 1.0
User-Agent: Mozilla Thunderbird
Content-Language: en-US
To: receiver@mail.org
Subject: some image
Envelope-To: <receiver@mail.org>
X-Spam-Flag: NO
UI-InboundReport: notjunk:1;M01:P0:4adGTmrKLvY=;aaHGOQyySHsYK/Gw5Ue7D9PTahmV

This is a multi-part message in MIME format.
--------------40Tk0emvCICBGcRiucnjKbPe
Content-Type: text/plain; charset=UTF-8; format=flowed
Content-Transfer-Encoding: 7bit


try this

--------------40Tk0emvCICBGcRiucnjKbPe
Content-Type: multipart/related;
 boundary="------------kY00i0RlbPzx0kpsduMUaVPZ"

--------------kY00i0RlbPzx0kpsduMUaVPZ
Content-Type: text/html; charset=UTF-8
Content-Transfer-Encoding: 7bit

<!DOCTYPE html>
<html>
  <head>

    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
  </head>
  <body>
    <p><img src="cid:part1.DePPID0S.dKVK0mlg@mail.com" alt=""></p>
    <p><br>
    </p>
    <p>try this<br>
    </p>
  </body>
</html>
--------------kY00i0RlbPzx0kpsduMUaVPZ
Content-Type: image/png; name="Z4md6xHlrYcKHhKK.png"
Content-Disposition: inline; filename="Z4md6xHlrYcKHhKK.png"
Content-Id: <part1.DePPID0S.dKVK0mlg@mail.com>
Content-Transfer-Encoding: base64

iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAYAAAD0eNT6AAAkw0lEQVR4AezdA8xlVxfG8f2x

--------------kY00i0RlbPzx0kpsduMUaVPZ--

--------------40Tk0emvCICBGcRiucnjKbPe--
""",
    b"""X-Mozilla-Status: 0001
X-Mozilla-Status2: 00000000
Return-Path: <david@emailproject.org>
Authentication-Results:  kundenserver.de; dkim=pass header.i=@emailproject.org
Received: from mail-ed1-f50.google.com ([209.85.208.50]) by mx.kundenserver.de
 (mxeue102 [217.72.192.67]) with ESMTPS (Nemesis) id 1M7dlr-1scXhf2XZl-000an0
 for <archiv@aderbauer.org>; Thu, 01 Aug 2024 15:35:54 +0200
Received: by mail-ed1-f50.google.com with SMTP id 4fb4d7f45d1cf-595856e2336so3510123a12.1
        for <archiv@aderbauer.org>; Thu, 01 Aug 2024 06:35:54 -0700 (PDT)
Received: from [192.168.178.190] (p4ffd7c0d.dip0.t-ipconnect.de. [79.253.124.13])
        by smtp.emailproject.org with ESMTPSA id 4fb4d7f45d1cf-5ac652911a5sm10057160a12.79.2024.08.01.06.35.53
        for <account@something.de>
        (version=TLS1_3 cipher=TLS_AES_128_GCM_SHA256 bits=128/128);
        Thu, 01 Aug 2024 06:35:53 -0700 (PDT)
From: David Aderbauer <david@emailproject.org>
Message-ID: <622b772d-0839-4ff3-9f31-2313b0b57040@emailproject.org>
Date: Thu, 1 Aug 2024 15:35:52 +0200
MIME-Version: 1.0
User-Agent: Mozilla Thunderbird
Content-Language: en-US
To: account@something.de
Subject: Testmail
Content-Type: text/plain; charset=UTF-8; format=flowed
Content-Transfer-Encoding: 8bit
Envelope-To: Account Name <account@something.de>
X-Spam-Flag: NO
UI-InboundReport: notjunk:1;M01:P0:Ugbg55Tfn70=;H/1hc/njG/PN7iylAI2fUL4TJkdq
 x5gY1l9zilKnfGRUGOzqplHb/79M2DDgbF3T0olQZp4yIxsJlp6iwyfMw1h98tfe1Q==

Hi

This is a test!

Viele Gruesse,

David

""",
]

TEST_EMAIL_PARAMETERS = [
    (
        TEST_EMAILS[0],
        "<e047e14d-2397-435b-baf6-8e8b7423f860@server.com>",
        "Whats up",
        1,
        3,
        5,
        "NO",
        "this a test to see how ur doin\n\n\n\n\n",
        "",
        22,
    ),
    (
        TEST_EMAILS[1],
        "<a634b121-4bc0-457d-a08f-a4579b9bb92a@mail.com>",
        "some image",
        1,
        2,
        4,
        "NO",
        "\ntry this\n",
        '<!DOCTYPE html>\n<html>\n  <head>\n\n    <meta http-equiv="content-type" content="text/html; charset=UTF-8">\n  </head>\n  <body>\n    <p><img src="cid:part1.DePPID0S.dKVK0mlg@mail.com" alt=""></p>\n    <p><br>\n    </p>\n    <p>try this<br>\n    </p>\n  </body>\n</html>',
        23,
    ),
    (
        TEST_EMAILS[2],
        "<622b772d-0839-4ff3-9f31-2313b0b57040@emailproject.org>",
        "Testmail",
        0,
        2,
        4,
        "NO",
        "Hi\n\nThis is a test!\n\nViele Gruesse,\n\nDavid\n\n",
        "",
        18,
    ),
]
