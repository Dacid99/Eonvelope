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

"""Test module for the :class:`FetchingCriterion` class."""

import datetime
from imaplib import Time2Internaldate

import pytest
from freezegun import freeze_time
from jmapc import EmailQueryFilterCondition

from core.constants import EmailFetchingCriterionChoices
from core.utils import FetchingCriterion
from test.core.utils.fetchers.test_ExchangeFetcher import mock_QuerySet


def test_FetchingCriterion__init__(faker):
    """Tests the constructor of :class:`core.utils.FetchingCriterion`."""
    args = faker.words(nb=2)

    result = FetchingCriterion(*args)

    assert result._criterion == args[0]
    assert result._argument == args[1]


def test_FetchingCriterion__str__():
    """Tests the __str__ method of :class:`core.utils.FetchingCriterion`."""
    assert str(FetchingCriterion("noarg", "")) == "noarg"
    assert str(FetchingCriterion("test with {}", "arg")) == "test with arg"


def test_FetchingCriterion__eq__():
    """Tests the __eq__ method of :class:`core.utils.FetchingCriterion`."""
    assert FetchingCriterion("value", "arg") == FetchingCriterion("value", "arg")
    assert FetchingCriterion("noarg ", "") == "noarg "
    assert FetchingCriterion("test with {}", "arg") == "test with {}"


def test_FetchingCriterion__hash__():
    """Tests the __hash__ method of :class:`core.utils.FetchingCriterion`."""
    assert hash(FetchingCriterion("value {}", "arg")) != hash(
        FetchingCriterion("value {}", "")
    )
    assert hash(FetchingCriterion("noarg", "")) != hash(FetchingCriterion("other", ""))


@pytest.mark.parametrize(
    "fetching_criterion",
    EmailFetchingCriterionChoices.values,
)
def test_FetchingCriterion_needs_argument(fetching_criterion):
    """Tests :func:`core.utils.FetchingCriterion.needs_argument`."""
    assert FetchingCriterion(fetching_criterion).needs_argument == (
        "{}" in fetching_criterion
    )


@pytest.mark.parametrize(
    "arg_fetching_criterion",
    [
        EmailFetchingCriterionChoices.BODY,
        EmailFetchingCriterionChoices.SUBJECT,
    ],
)
def test_FetchingCriterion_validate__missing_arg(arg_fetching_criterion):
    """Tests :class:`core.utils.FetchingCriterion.validate`
    in case of missing argument.
    """
    with pytest.raises(ValueError):  # noqa: PT011 # no good match to check
        FetchingCriterion(arg_fetching_criterion).validate()


@pytest.mark.parametrize(
    ("int_arg_fetching_criterion", "bad_int_arg"),
    [
        (EmailFetchingCriterionChoices.LARGER, "not an integer"),
        (EmailFetchingCriterionChoices.SMALLER, "-405"),
    ],
)
def test_FetchingCriterion_validate__bad_int(int_arg_fetching_criterion, bad_int_arg):
    """Tests :class:`core.utils.FetchingCriterion.validate`
    in case of a bad integer argument.
    """
    with pytest.raises(ValueError):  # noqa: PT011 # no good match to check
        FetchingCriterion(int_arg_fetching_criterion, bad_int_arg).validate()


@pytest.mark.parametrize(
    "date_arg_fetching_criterion", [EmailFetchingCriterionChoices.SENTSINCE]
)
def test_FetchingCriterion_validate__bad_date(date_arg_fetching_criterion):
    """Tests :class:`core.utils.FetchingCriterion.validate`
    in case of a bad date argument.
    """
    with pytest.raises(ValueError):  # noqa: PT011 # no good match to check
        FetchingCriterion(date_arg_fetching_criterion, "no datetime").validate()


@pytest.mark.parametrize(
    ("criterion_name", "expected_time_delta"),
    [
        (EmailFetchingCriterionChoices.DAILY, datetime.timedelta(days=1)),
        (EmailFetchingCriterionChoices.WEEKLY, datetime.timedelta(weeks=1)),
        (EmailFetchingCriterionChoices.MONTHLY, datetime.timedelta(weeks=4)),
        (EmailFetchingCriterionChoices.ANNUALLY, datetime.timedelta(weeks=52)),
    ],
)
def test_IMAP4Fetcher_make_fetching_criterion_date_criterion(
    faker, criterion_name, expected_time_delta
):
    """Tests :func:`core.utils.FetchingCriterion.as_imap_criterion`
    in different cases of date criteria.
    """
    fake_datetime = faker.date_time_this_decade(tzinfo=datetime.UTC)
    expected_criterion = f"SENTSINCE {Time2Internaldate(fake_datetime - expected_time_delta).split(' ')[0].strip('" ')}"

    with freeze_time(fake_datetime):
        result = FetchingCriterion(criterion_name, "value").as_imap_criterion()

    assert result == expected_criterion


def test_IMAP4Fetcher_make_fetching_criterion_sentsince():
    """Tests :func:`core.utils.FetchingCriterion.as_imap_criterion`
    in different cases of date criteria.
    """
    result = FetchingCriterion(
        EmailFetchingCriterionChoices.SENTSINCE, "2009-01-12"
    ).as_imap_criterion()

    assert result == "SENTSINCE 12-Jan-2009"


@pytest.mark.parametrize(
    ("criterion_name", "expected_result"),
    [
        (EmailFetchingCriterionChoices.ALL, "ALL"),
        (EmailFetchingCriterionChoices.UNSEEN, "UNSEEN"),
        (EmailFetchingCriterionChoices.SEEN, "SEEN"),
        (EmailFetchingCriterionChoices.RECENT, "RECENT"),
        (EmailFetchingCriterionChoices.NEW, "NEW"),
        (EmailFetchingCriterionChoices.OLD, "OLD"),
        (EmailFetchingCriterionChoices.FLAGGED, "FLAGGED"),
        (EmailFetchingCriterionChoices.UNFLAGGED, "UNFLAGGED"),
        (EmailFetchingCriterionChoices.DRAFT, "DRAFT"),
        (EmailFetchingCriterionChoices.UNDRAFT, "UNDRAFT"),
        (EmailFetchingCriterionChoices.DELETED, "DELETED"),
        (EmailFetchingCriterionChoices.UNDELETED, "UNDELETED"),
        (EmailFetchingCriterionChoices.ANSWERED, "ANSWERED"),
        (EmailFetchingCriterionChoices.UNANSWERED, "UNANSWERED"),
    ],
)
def test_FetchingCriterion_as_imap_criterion__no_arg(criterion_name, expected_result):
    """Tests :func:`core.utils.FetchingCriterion.as_imap_criterion`
    in different cases of non-date criteria.
    """
    result = FetchingCriterion(criterion_name, "value").as_imap_criterion()

    assert result == expected_result


@pytest.mark.parametrize(
    ("criterion_name", "expected_result_template"),
    [
        (EmailFetchingCriterionChoices.SUBJECT, "SUBJECT {}"),
        (EmailFetchingCriterionChoices.KEYWORD, "KEYWORD {}"),
        (EmailFetchingCriterionChoices.UNKEYWORD, "UNKEYWORD {}"),
        (EmailFetchingCriterionChoices.LARGER, "LARGER {}"),
        (EmailFetchingCriterionChoices.SMALLER, "SMALLER {}"),
        (EmailFetchingCriterionChoices.BODY, "BODY {}"),
        (EmailFetchingCriterionChoices.FROM, "FROM {}"),
    ],
)
def test_FetchingCriterion_as_imap_criterion_with_arg(
    faker, criterion_name, expected_result_template
):
    """Tests :func:`core.utils.FetchingCriterion.as_imap_criterion`
    in different cases of non-date criteria.
    """
    fake_criterion_arg = faker.word()
    result = FetchingCriterion(criterion_name, fake_criterion_arg).as_imap_criterion()

    assert result == expected_result_template.format(fake_criterion_arg)


@pytest.mark.parametrize(
    ("criterion_name", "expected_time_delta"),
    [
        (EmailFetchingCriterionChoices.DAILY, datetime.timedelta(days=1)),
        (EmailFetchingCriterionChoices.WEEKLY, datetime.timedelta(weeks=1)),
        (EmailFetchingCriterionChoices.MONTHLY, datetime.timedelta(weeks=4)),
        (EmailFetchingCriterionChoices.ANNUALLY, datetime.timedelta(weeks=52)),
    ],
)
def test_FetchingCriterion_as_jmap_filter_date_criterion(
    faker, criterion_name, expected_time_delta
):
    """Tests :func:`core.utils.FetchingCriterion.as_jmap_filter`
    in different cases of date criteria.
    """
    fake_datetime = faker.date_time_this_decade(tzinfo=datetime.UTC)
    expected_filter = EmailQueryFilterCondition(
        after=fake_datetime - expected_time_delta
    )

    with freeze_time(fake_datetime):
        result = FetchingCriterion(criterion_name, "value").as_jmap_filter()

    assert result == expected_filter


def test_FetchingCriterion_as_jmap_filter__sentsince():
    """Tests :func:`core.utils.FetchingCriterion.as_jmap_filter`
    in case of the sentsince criterion.
    """
    result = FetchingCriterion(
        EmailFetchingCriterionChoices.SENTSINCE, "2013-05-29"
    ).as_jmap_filter()
    assert result == EmailQueryFilterCondition(
        after=datetime.datetime(2013, 5, 29, tzinfo=datetime.UTC)
    )


@pytest.mark.parametrize(
    ("criterion_name", "expected_filter_kwarg"),
    [
        (EmailFetchingCriterionChoices.ALL, {}),
        (EmailFetchingCriterionChoices.SEEN, {"has_keyword": "$seen"}),
        (EmailFetchingCriterionChoices.DRAFT, {"has_keyword": "$draft"}),
        (EmailFetchingCriterionChoices.ANSWERED, {"has_keyword": "$answered"}),
        (EmailFetchingCriterionChoices.UNSEEN, {"not_keyword": "$seen"}),
        (EmailFetchingCriterionChoices.UNDRAFT, {"not_keyword": "$draft"}),
        (EmailFetchingCriterionChoices.UNANSWERED, {"not_keyword": "$answered"}),
    ],
)
def test_FetchingCriterion_as_jmap_filter__no_arg(
    criterion_name, expected_filter_kwarg
):
    """Tests :func:`core.utils.FetchingCriterion.as_jmap_filter`
    in different cases of criteria without argument.
    """
    result = FetchingCriterion(criterion_name, "").as_jmap_filter()

    assert result == EmailQueryFilterCondition(**expected_filter_kwarg)


@pytest.mark.parametrize(
    ("criterion_name", "criterion_arg", "expected_filter_kwarg"),
    [
        (EmailFetchingCriterionChoices.LARGER, 140, {"min_size": 140}),
        (EmailFetchingCriterionChoices.SMALLER, 598, {"max_size": 598}),
        (EmailFetchingCriterionChoices.BODY, "testtext", {"body": "testtext"}),
        (
            EmailFetchingCriterionChoices.FROM,
            "sender@server.com",
            {"mail_from": "sender@server.com"},
        ),
    ],
)
def test_FetchingCriterion_as_jmap_filter__with_arg(
    criterion_name, criterion_arg, expected_filter_kwarg
):
    """Tests :func:`core.utils.FetchingCriterion.as_jmap_filter`
    in different cases of criteria with argument.
    """
    result = FetchingCriterion(criterion_name, criterion_arg).as_jmap_filter()

    assert result == EmailQueryFilterCondition(**expected_filter_kwarg)


@pytest.mark.parametrize(
    ("criterion_name", "expected_time_delta"),
    [
        (EmailFetchingCriterionChoices.DAILY, datetime.timedelta(days=1)),
        (EmailFetchingCriterionChoices.WEEKLY, datetime.timedelta(weeks=1)),
        (EmailFetchingCriterionChoices.MONTHLY, datetime.timedelta(weeks=4)),
        (EmailFetchingCriterionChoices.ANNUALLY, datetime.timedelta(weeks=52)),
    ],
)
def test_FetchingCriterion_as_exchange_queryset__date_criterion(
    faker, mock_QuerySet, criterion_name, expected_time_delta
):
    """Tests :func:`core.utilsFetchingCriterion.as_exchange_queryset`
    in different cases of date criteria.
    """
    fake_datetime = faker.date_time_this_decade(tzinfo=datetime.UTC)

    with freeze_time(fake_datetime):
        result = FetchingCriterion(criterion_name, "").as_exchange_queryset(
            mock_QuerySet
        )

    assert result == mock_QuerySet.filter.return_value
    mock_QuerySet.filter.assert_called_once_with(
        datetime_received__gte=fake_datetime - expected_time_delta
    )


def test_FetchingCriterion_as_exchange_queryset__sentsince_criterion(mock_QuerySet):
    """Tests :func:`core.utilsFetchingCriterion.as_exchange_queryset`
    in different cases of date criteria.
    """

    result = FetchingCriterion(
        EmailFetchingCriterionChoices.SENTSINCE, "2010-6-5"
    ).as_exchange_queryset(mock_QuerySet)

    assert result == mock_QuerySet.filter.return_value
    mock_QuerySet.filter.assert_called_once_with(
        datetime_received__gte=datetime.datetime(2010, 6, 5, tzinfo=datetime.UTC)
    )


@pytest.mark.parametrize(
    ("criterion_name", "criterion_arg", "expected_kwarg"),
    [
        (EmailFetchingCriterionChoices.UNSEEN, "", {"is_read": False}),
        (EmailFetchingCriterionChoices.SEEN, "", {"is_read": True}),
        (EmailFetchingCriterionChoices.DRAFT, "", {"is_draft": True}),
        (EmailFetchingCriterionChoices.UNDRAFT, "", {"is_draft": False}),
        (
            EmailFetchingCriterionChoices.SUBJECT,
            "somestring",
            {"subject__contains": "somestring"},
        ),
        (
            EmailFetchingCriterionChoices.BODY,
            "textPart",
            {"body__contains": "textPart"},
        ),
    ],
)
def test_FetchingCriterion_as_exchange_queryset__other_criterion(
    mock_QuerySet, criterion_name, criterion_arg, expected_kwarg
):
    """Tests :func:`core.utilsFetchingCriterion.as_exchange_queryset`
    in different cases of flag criteria.
    """
    result = FetchingCriterion(criterion_name, criterion_arg).as_exchange_queryset(
        mock_QuerySet
    )

    assert result == mock_QuerySet.filter.return_value
    mock_QuerySet.filter.assert_called_once_with(**expected_kwarg)


def test_FetchingCriterion_as_exchange_queryset__all_criterion(mock_QuerySet):
    """Tests :func:`core.utilsFetchingCriterion.as_exchange_queryset`
    in case of the ALL criterion.
    """
    result = FetchingCriterion(
        EmailFetchingCriterionChoices.ALL, ""
    ).as_exchange_queryset(mock_QuerySet)

    assert result == mock_QuerySet
