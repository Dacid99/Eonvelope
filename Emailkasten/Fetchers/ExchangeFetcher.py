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

"""Module with the :class:`ExchangeFetcher` class."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Literal

import exchangelib

from .. import constants
from ..ExchangeMailParser import ExchangeMailParser

if TYPE_CHECKING:
    from types import TracebackType


class ExchangeFetcher:
    PROTOCOL = constants.MailFetchingProtocols.EXCHANGE

    AVAILABLE_FETCHING_CRITERIA = [
        constants.MailFetchingCriteria.ALL,
        constants.MailFetchingCriteria.UNSEEN,
        constants.MailFetchingCriteria.RECENT,
        constants.MailFetchingCriteria.NEW,
        constants.MailFetchingCriteria.OLD,
        constants.MailFetchingCriteria.FLAGGED,
        constants.MailFetchingCriteria.DRAFT,
        constants.MailFetchingCriteria.ANSWERED,
        constants.MailFetchingCriteria.DAILY,
        constants.MailFetchingCriteria.WEEKLY,
        constants.MailFetchingCriteria.MONTHLY,
        constants.MailFetchingCriteria.ANNUALLY
    ]

    def __init__(self, username, password, primary_smtp_address=None, server='outlook.office365.com', fullname=None, access_type=exchangelib.DELEGATE, autodiscover=True, locale=None, default_timezone=None):
        self.logger = logging.getLogger(__name__)

        self.__credentials = exchangelib.Credentials(username, password)
        self.__config = exchangelib.Configuration(server=server, credentials=self.__credentials)

        self.__mailhost = exchangelib.Account(
            primary_smtp_address=primary_smtp_address,
            fullname=fullname,
            access_type=access_type,
            autodiscover=autodiscover,
            locale=locale,
            default_timezone=default_timezone
            )

    def fetchAllAndPrint(self):
        for message in self.__mailhost.inbox.all().order_by('-datetime_received')[:10]:
            mailParser = ExchangeMailParser(message)
            print(mailParser.parseFrom())


    def close(self):
        pass

    def __enter__(self) -> ExchangeFetcher:
        """Framework method for use of class in 'with' statement, creates an instance."""
        self.logger.debug(str(self.__class__.__name__) + "._enter_")
        return self


    def __exit__(self, exc_type: BaseException|None, exc_value: BaseException|None, traceback: TracebackType|None) -> Literal[True]:
        """Framework method for use of class in 'with' statement, closes an instance.

        Args:
            exc_type: The exception type that raised close.
            exc_value: The exception value that raised close.
            traceback: The exception traceback that raised close.

        Returns:
            True, exceptions are consumed.
        """
        self.logger.debug("Exiting")
        self.close()
        if exc_value or exc_type:
            self.logger.error("Unexpected error %s occured!", exc_type, exc_info=exc_value)
        return True
