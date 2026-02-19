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

"""Module with the :class:`FetchingCriterion` utility class."""

import imaplib
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import jmapc
from django.utils.translation import gettext_lazy as _

from core.constants import INTERNAL_DATE_FORMAT, EmailFetchingCriterionChoices

if TYPE_CHECKING:
    from exchangelib.queryset import QuerySet


class FetchingCriterion:
    """Class encapsulating the fetching-criterion logic."""

    def __init__(
        self, criterion: EmailFetchingCriterionChoices, argument: str = ""
    ) -> None:
        """Constructor.

        Args:
            criterion: One of the class:`core.constants.EmailFetchingCriterionChoices`.
            argument: Argument for the criterion. Defaults to "".
        """
        self._criterion = criterion
        self._argument = argument

    def __str__(self) -> str:
        """The formatted criterion as a string.

        Returns:
            The formatted string criterion.
        """
        return self._criterion.format(self._argument)

    def __eq__(self, value: object) -> bool:
        """Checks for equality.

        Important:
            For another FetchingCriterion instance the formatted criteria are compared, for a string only the criteria.
            Otherwise equality checks to the :class:`EmailFetchingCriterionChoices` members don't work.

        Returns:
            Whether this fetching criterion is equal to another object.
        """
        if isinstance(value, FetchingCriterion):
            return str(self) == str(value)
        if isinstance(value, str):
            return self._criterion == value
        return False

    def __hash__(self) -> int:
        """Creates a hash for this object."""
        return hash(str(self))

    def validate(self) -> None:
        """Checks if this fetching criterion is valid.

        Note:
            Things that are NOT validated here:
            - Availability of the criterion for the mailbox of fetcher.
            - Existence of the criterion in general (covered by checking the above)

        Raises:
            ValidationError: If this fetching criterion is invalid.
        """
        if self.needs_argument and not self._argument:
            raise ValueError(_("This fetching criterion requires an argument."))
        if self._criterion == EmailFetchingCriterionChoices.SENTSINCE:
            try:
                datetime.strptime(  # noqa: DTZ007 # this value does not need to be naive
                    self._argument, INTERNAL_DATE_FORMAT
                )
            except ValueError as error:
                raise ValueError(
                    _("Date values must be given in format %(format)s.")
                    % {"format": INTERNAL_DATE_FORMAT}
                ) from error
        if self._criterion in [
            EmailFetchingCriterionChoices.SMALLER,
            EmailFetchingCriterionChoices.LARGER,
        ]:
            try:
                size_int = int(self._argument)
            except ValueError as error:
                raise ValueError(_("This value must be an integer.")) from error
            if size_int < 0:
                raise ValueError(_("This value must be a positive number."))

    def as_imap_criterion(self) -> str:
        """Returns the formatted criterion for the IMAP request, handles dates in particular.

        Note:
            There's no need to use timezone.now here as only the date part is used.

        Returns:
            Formatted criterion to be used in IMAP request.
        """
        match self._criterion:
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
                    self._argument, INTERNAL_DATE_FORMAT
                ).astimezone(UTC)
            case _:
                return str(self)
        return EmailFetchingCriterionChoices.SENTSINCE.format(
            imaplib.Time2Internaldate(start_time).split(" ")[0].strip('" ')
        )

    def as_jmap_filter(self) -> jmapc.EmailQueryFilterCondition:
        """Returns the filter-condition for the JMAP Email/query request.

        Returns:
            The filter-condition to be used in JMAP request.
        """
        match self._criterion:
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
                    self._argument, INTERNAL_DATE_FORMAT
                ).astimezone(UTC)
            case (
                EmailFetchingCriterionChoices.SEEN
                | EmailFetchingCriterionChoices.ANSWERED
                | EmailFetchingCriterionChoices.DRAFT
            ):
                return jmapc.EmailQueryFilterCondition(
                    has_keyword="$" + self._criterion.lower(),
                )
            case (
                EmailFetchingCriterionChoices.UNSEEN
                | EmailFetchingCriterionChoices.UNANSWERED
                | EmailFetchingCriterionChoices.UNDRAFT
            ):
                return jmapc.EmailQueryFilterCondition(
                    not_keyword="$" + self._criterion.lower().removeprefix("un"),
                )
            case EmailFetchingCriterionChoices.LARGER:
                return jmapc.EmailQueryFilterCondition(min_size=int(self._argument))
            case EmailFetchingCriterionChoices.SMALLER:
                return jmapc.EmailQueryFilterCondition(max_size=int(self._argument))
            case EmailFetchingCriterionChoices.BODY:
                return jmapc.EmailQueryFilterCondition(body=self._argument)
            case EmailFetchingCriterionChoices.FROM:
                return jmapc.EmailQueryFilterCondition(mail_from=self._argument)
            case _:  # only ALL left
                return jmapc.EmailQueryFilterCondition()
        return jmapc.EmailQueryFilterCondition(after=start_time)

    def as_exchange_queryset(self, base_query: QuerySet) -> QuerySet:
        """Returns the queryset for the Exchange request.

        Note:
            Use no timezone here to use the mailserver time settings.

        Args:
            base_query: The query to extend based on the criterion.

        Returns:
            Augmented queryset to be used in Exchange request.
        """
        match self._criterion:
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
                    self._argument, INTERNAL_DATE_FORMAT
                ).astimezone(UTC)
            case EmailFetchingCriterionChoices.SUBJECT:
                return base_query.filter(subject__contains=self._argument)
            case EmailFetchingCriterionChoices.BODY:
                return base_query.filter(body__contains=self._argument)
            case EmailFetchingCriterionChoices.UNSEEN:
                return base_query.filter(is_read=False)
            case EmailFetchingCriterionChoices.SEEN:
                return base_query.filter(is_read=True)
            case EmailFetchingCriterionChoices.DRAFT:
                return base_query.filter(is_draft=True)
            case EmailFetchingCriterionChoices.UNDRAFT:
                return base_query.filter(is_draft=False)
            case _:  # only ALL left
                return base_query
        return base_query.filter(datetime_received__gte=start_time)

    @property
    def needs_argument(self) -> bool:
        """Whether this fetching criterion requires an argument.

        Returns:
           Whether this fetching criterion is different after formatting.
        """
        return self._criterion.format("") != self._criterion
