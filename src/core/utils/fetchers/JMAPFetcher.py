# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Eonvelope - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Eonvelope Contributors
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

"""Module with the :class:`JMAPFetcher` class."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, override

import jmapc
import requests

from core.constants import (
    INTERNAL_DATE_FORMAT,
    EmailFetchingCriterionChoices,
    EmailProtocolChoices,
)

from .BaseFetcher import BaseFetcher
from .exceptions import BadServerResponseError, MailAccountError, MailboxError


if TYPE_CHECKING:
    from core.models.Account import Account
    from core.models.Email import Email
    from core.models.Mailbox import Mailbox


class JMAPFetcher(BaseFetcher):
    """Maintains a connection to the JMAP server and fetches data using :mod:`jmapc`.

    Opens a connection to the JMAP server on construction and is preferably used in a 'with' environment.
    Allows fetching of mails and mailboxes from an account on an JMAP host.
    """

    PROTOCOL = EmailProtocolChoices.JMAP
    """Name of the used protocol, refers to :attr:`MailFetchingProtocols.JMAP`."""

    AVAILABLE_FETCHING_CRITERIA = (
        EmailFetchingCriterionChoices.ALL,
        EmailFetchingCriterionChoices.SEEN,
        EmailFetchingCriterionChoices.UNSEEN,
        EmailFetchingCriterionChoices.DRAFT,
        EmailFetchingCriterionChoices.UNDRAFT,
        EmailFetchingCriterionChoices.ANSWERED,
        EmailFetchingCriterionChoices.UNANSWERED,
        EmailFetchingCriterionChoices.DAILY,
        EmailFetchingCriterionChoices.WEEKLY,
        EmailFetchingCriterionChoices.MONTHLY,
        EmailFetchingCriterionChoices.ANNUALLY,
        EmailFetchingCriterionChoices.BODY,
        EmailFetchingCriterionChoices.FROM,
        EmailFetchingCriterionChoices.SENTSINCE,
        EmailFetchingCriterionChoices.LARGER,
        EmailFetchingCriterionChoices.SMALLER,
    )
    """Tuple of all criteria available for fetching. Refers to :class:`MailFetchingCriteria`.
    Must be immutable!
    """

    @staticmethod
    def make_fetching_filter(
        criterion_name: str, criterion_arg: str
    ) -> jmapc.EmailQueryFilterCondition:
        """Returns the filter-condition for the JMAP Email/query request.

        Args:
            criterion: The criterion for the JMAP request.
            criterion_arg: The argument for the criterion.
            base_query: The query to extend based on the criterion.

        Returns:
            The filter-condition to be used in JMAP request.
        """
        match criterion_name:
            case EmailFetchingCriterionChoices.DAILY:
                start_time = datetime.now(tz=UTC) - timedelta(days=1)
            case EmailFetchingCriterionChoices.WEEKLY:
                start_time = datetime.now(tz=UTC) - timedelta(weeks=1)
            case EmailFetchingCriterionChoices.MONTHLY:
                start_time = datetime.now(tz=UTC) - timedelta(weeks=4)
            case EmailFetchingCriterionChoices.ANNUALLY:
                start_time = datetime.now(tz=UTC) - timedelta(weeks=52)
            case EmailFetchingCriterionChoices.SENTSINCE:
                start_time = datetime.strptime(
                    criterion_arg, INTERNAL_DATE_FORMAT
                ).astimezone(UTC)
            case (
                EmailFetchingCriterionChoices.SEEN
                | EmailFetchingCriterionChoices.ANSWERED
                | EmailFetchingCriterionChoices.DRAFT
            ):
                return jmapc.EmailQueryFilterCondition(
                    has_keyword="$" + criterion_name.lower(),
                )
            case (
                EmailFetchingCriterionChoices.UNSEEN
                | EmailFetchingCriterionChoices.UNANSWERED
                | EmailFetchingCriterionChoices.UNDRAFT
            ):
                return jmapc.EmailQueryFilterCondition(
                    not_keyword="$" + criterion_name.lower().removeprefix("un"),
                )
            case EmailFetchingCriterionChoices.LARGER:
                return jmapc.EmailQueryFilterCondition(min_size=int(criterion_arg))
            case EmailFetchingCriterionChoices.SMALLER:
                return jmapc.EmailQueryFilterCondition(max_size=int(criterion_arg))
            case EmailFetchingCriterionChoices.BODY:
                return jmapc.EmailQueryFilterCondition(body=criterion_arg)
            case EmailFetchingCriterionChoices.FROM:
                return jmapc.EmailQueryFilterCondition(mail_from=criterion_arg)
            case _:
                return jmapc.EmailQueryFilterCondition()
        return jmapc.EmailQueryFilterCondition(after=start_time)

    @override
    def __init__(self, account: Account) -> None:
        super().__init__(account)
        self.connect_to_host()

    @override
    def connect_to_host(self) -> None:
        try:
            if self.account.mail_address:
                self._mail_client = jmapc.Client.create_with_password(
                    host=self.account.mail_host_address,
                    user=self.account.mail_address,
                    password=self.account.password,
                )
            else:
                self._mail_client = jmapc.Client.create_with_api_token(
                    host=self.account.mail_host_address,
                    api_token=self.account.password,
                )
        except requests.RequestException as error:
            self.logger.exception("Error connecting to %s!", self.account)
            raise MailAccountError(error, "login") from error
        self.logger.info("Successfully connected to %s.", self.account)

    @override
    def test(self, mailbox: Mailbox | None = None) -> None:
        super().test(mailbox)

        method = jmapc.methods.IdentityGet()
        self.logger.debug("Testing %s ...", self.account)
        try:
            result = self._mail_client.request(method)
        except requests.RequestException as error:
            self.logger.exception("Error connecting to %s!", self.account)
            raise MailAccountError(error) from error
        except jmapc.ClientError as error:
            self.logger.exception(
                "Wrong number of responses for request to %s!", self.account
            )
            raise MailAccountError(
                BadServerResponseError(str(error)), method.jmap_method_name
            ) from error
        if not isinstance(result, jmapc.methods.IdentityGetResponse):
            self.logger.error("Error in response from %s!", self.account)
            raise MailAccountError(
                BadServerResponseError(result.to_json()), method.jmap_method_name
            )
        self.logger.debug("Successfully tested %s.", self.account)

        if mailbox is not None:
            methods = (
                jmapc.methods.MailboxQuery(
                    filter=jmapc.MailboxQueryFilterCondition(name=mailbox.name)
                ),
                jmapc.methods.MailboxGet(ids=jmapc.Ref("/ids")),
            )
            self.logger.debug("Testing %s ...", mailbox)
            try:
                results = self._mail_client.request(methods)
            except requests.RequestException as error:
                self.logger.exception("Error connecting to %s!", self.account)
                raise MailboxError(error) from error
            if not isinstance(results[1].response, jmapc.methods.MailboxGetResponse):
                self.logger.error("Error in response from %s!", self.account)
                raise MailboxError(
                    BadServerResponseError(results[1].response.to_json()),
                    methods[1].jmap_method_name,
                )
            self.logger.debug("Successfully tested %s.", mailbox)

    @override
    def fetch_emails(
        self,
        mailbox: Mailbox,
        criterion: str = EmailFetchingCriterionChoices.ALL,
        criterion_arg: str = "",
    ) -> list[bytes]:
        super().fetch_emails(mailbox, criterion)

        self.logger.debug(
            "Searching and fetching %s messages in %s...",
            criterion,
            mailbox,
        )

        method = jmapc.methods.MailboxQuery(
            filter=jmapc.MailboxQueryFilterCondition(name=mailbox.name)
        )
        self.logger.debug("Querying for mailbox %s ...", mailbox)
        try:
            result = self._mail_client.request(method)
        except requests.RequestException as error:
            self.logger.exception("Error connecting to %s!", self.account)
            raise MailAccountError(error) from error
        except jmapc.ClientError as error:
            self.logger.exception(
                "Wrong number of responses for request to %s!", self.account
            )
            raise MailAccountError(
                BadServerResponseError(str(error)), method.jmap_method_name
            ) from error
        if not isinstance(result, jmapc.methods.MailboxQueryResponse):
            self.logger.error("Error in response from %s!", self.account)
            raise MailAccountError(BadServerResponseError(result.to_json()), "")
        if not result.ids or not isinstance(result.ids, list):
            raise MailboxError(IndexError("Mailbox not found"))
        self.logger.debug("Successfully queried mailbox.")

        criterion_filter = self.make_fetching_filter(criterion, criterion_arg)
        criterion_filter.in_mailbox = result.ids[0]
        methods = (
            jmapc.methods.EmailQuery(
                sort=[jmapc.Comparator(property="receivedAt", is_ascending=True)],
                filter=criterion_filter,
            ),
            jmapc.methods.EmailGet(
                ids=jmapc.Ref("/ids"),
                properties=[
                    "blobId",
                ],
            ),
        )
        self.logger.debug("Querying %s messages in %s ...", criterion, mailbox)
        try:
            results = self._mail_client.request(methods)
        except requests.RequestException as error:
            self.logger.exception("Error connecting to %s!", self.account)
            raise MailAccountError(error) from error
        if not isinstance(results[1].response, jmapc.methods.EmailGetResponse):
            self.logger.error("Error in response from %s!", self.account)
            raise MailboxError(
                BadServerResponseError(results[1].response.to_json()),
                methods[1].jmap_method_name,
            )
        self.logger.info(
            "Found %s messages matching %s in %s.",
            len(results[1].response.data),
            criterion,
            mailbox,
        )

        email_data = []
        self.logger.debug("Downloading matching message blobs from %s ...", mailbox)
        for email in results[1].response.data:
            blob_url = self._mail_client.jmap_session.download_url.format(
                accountId=self._mail_client.account_id,
                blobId=email.blob_id,
                name="",
                type="message/rfc822",
            )
            try:
                response = self._mail_client.requests_session.get(
                    blob_url, stream=True, timeout=self.account.timeout
                )
                response.raise_for_status()
            except requests.RequestException as error:
                self.logger.exception("Error connecting to %s!", self.account)
                raise MailAccountError(error) from error
            email_data.append(response.raw.data)
            self.logger.debug("Successfully downloaded message blobs.")
        return email_data

    @override
    def fetch_mailboxes(self) -> list[tuple[str, str]]:
        method = jmapc.methods.MailboxGet(ids=None, properties=["name", "role"])
        self.logger.debug("Fetching mailboxes in %s ...", self.account)
        try:
            result = self._mail_client.request(method)
        except requests.RequestException as error:
            self.logger.exception("Error connecting to %s!", self.account)
            raise MailAccountError(error) from error
        except jmapc.ClientError as error:
            self.logger.exception(
                "Wrong number of responses for request to %s!", self.account
            )
            raise MailAccountError(
                BadServerResponseError(str(error)), method.jmap_method_name
            ) from error
        if not isinstance(result, jmapc.methods.MailboxGetResponse):
            self.logger.error("Error in response from %s!", self.account)
            raise MailAccountError(
                BadServerResponseError(result.to_json()), method.jmap_method_name
            )
        self.logger.debug("Successfully fetched mailboxes in %s.", self.account)
        return [
            (mailbox.name, mailbox.role or "")
            for mailbox in result.data
            if mailbox.name is not None
        ]

    @override
    def restore(self, email: Email) -> None:
        super().restore(email)
        if not email.file_path:
            raise FileNotFoundError("This email has no stored eml file.")
        self.logger.debug("Uploading blob for %s ...", email)
        try:
            blob = self._mail_client.upload_blob(file_name=email.absolute_filepath)
        except requests.RequestException as error:
            self.logger.exception("Error connecting to %s!", self.account)
            raise MailAccountError(error) from error
        self.logger.debug("Successfully uploaded email blob.")
        methods = (
            jmapc.methods.MailboxQuery(
                filter=jmapc.MailboxQueryFilterCondition(name=email.mailbox.name)
            ),
            jmapc.methods.CustomMethod(
                {
                    "emails": {
                        1: {
                            "blobId": blob.id,
                            "#mailboxIds": {
                                "path": "/ids",
                                "resultOf": "0.Mailbox/query",
                                "name": "Mailbox/query",
                            },
                        }
                    }
                }
            ),
        )
        methods[1].jmap_method = "Email/import"
        self.logger.debug("Importing %s to its mailbox ...", email)
        try:
            results = self._mail_client.request(methods)
        except requests.RequestException as error:
            self.logger.exception("Error connecting to %s!", self.account)
            raise MailAccountError(error) from error
        if not isinstance(results[1].response, jmapc.methods.CustomResponse):
            self.logger.error("Error in response from %s!", self.account)
            raise MailboxError(
                BadServerResponseError(results[1].response.to_json()),
                methods[1].jmap_method_name,
            )
        self.logger.debug("Successfully imported email.")

    @override
    def close(self) -> None:
        """No cleanup of :class:`jmapc.Client` required."""
