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

"""Module with the constant values for the :mod:`Emailkasten` modules."""

import os
from typing import Final


class MailFetchingCriteria:
    """Namespace class for all implemented mail fetching criteria constants.
    For a list of all existing IMAP criteria see https://datatracker.ietf.org/doc/html/rfc3501.html#section-6.4.4
    Note that IMAP does not support time just dates. So we are always refering to full days.
    POP does not support queries at all, so everything will be fetched."""

    RECENT: Final[str] = "RECENT"
    """Filter: str by "RECENT" flag."""

    UNSEEN: Final[str] = "UNSEEN"
    """Filter by "UNSEEN" flag."""

    ALL: Final[str] = "ALL"
    """Filter by "ALL" flag."""

    NEW: Final[str] = "NEW"
    """Filter by "NEW" flag."""

    OLD: Final[str] = "OLD"
    """Filter by "OLD" flag."""

    FLAGGED: Final[str] = "FLAGGED"
    """Filter by "FLAGGED" flag."""

    DRAFT: Final[str] = "DRAFT"
    """Filter by "DRAFT" flag."""

    ANSWERED: Final[str] = "ANSWERED"
    """Filter by "ANSWERED" flag."""

    DAILY: Final[str] = "DAILY"
    """Filter using "SENTSINCE" for mails sent the previous day or later."""

    WEEKLY: Final[str] = "WEEKLY"
    """Filter using "SENTSINCE" for mails sent the previous week (counting back from now) or later."""

    MONTHLY: Final[str] = "MONTHLY"
    """Filter using "SENTSINCE" for mails sent the previous 4 weeks (counting back from now) or later."""

    ANNUALLY: Final[str] = "ANNUALLY"
    """Filter using "SENTSINCE" for mails sent the previous 52 weeks (counting back from now) or later."""

    def __iter__(self):
        """Method to allow easier referencing of the members by listing.
        Note:
            value must come first in the listed tuples to match the format for field choices.
        """
        return iter(
            (value, attr)
            for attr, value in self.__class__.__dict__.items()
            if not attr.startswith("__")
        )

    def __getitem__(self, key):
        return getattr(self, key)


class MailFetchingProtocols:
    """Namespace class for all implemented mail protocols constants."""

    IMAP: Final[str] = "IMAP"
    """The IMAP4 protocol."""

    IMAP_SSL: Final[str] = "IMAP_SSL"
    """The IMAP4 protocol over SSL."""

    POP3: Final[str] = "POP3"
    """The POP3 protocol."""

    POP3_SSL: Final[str] = "POP3_SSL"
    """The POP3 protocol over SSL."""

    EXCHANGE: Final[str] = "EXCHANGE"
    """Microsofts Exchange protocol."""

    def __iter__(self):
        """Method to allow easier referencing of the members by listing.
        Note:
            value must come first in the listed tuples to match the format for field choices.
        """
        return iter(
            (value, attr)
            for attr, value in self.__class__.__dict__.items()
            if not attr.startswith("__")
        )

    def __getitem__(self, key):
        return getattr(self, key)


class TestStatusCodes:
    """Namespace class for all status codes for the tests of mailaccounts and mailboxes."""

    OK: Final[int] = 0
    """Everything worked fine"""

    ABORTED: Final[int] = 1
    """The operation was aborted, try again."""

    BAD_RESPONSE: Final[int] = 2
    """The server did not return status OK."""

    ERROR: Final[int] = 3
    """There was an IMAP error, the account is unhealthy."""

    UNEXPECTED_ERROR: Final[int] = 4
    """An unexpected error occured, try again and check the logs."""

    INFOS: Final[list[str]] = [
        "Everything worked as expected.",
        "The operation was aborted, please try again.",
        "The server returned a bad status, the unhealthy flag set.",
        "There was an error, the unhealthy flag set.",
        "An unexpected error occured, please try again and check the logs.",
    ]


class FilterSetups:
    """Namespace class for all filter setups for different field types."""

    TEXT: Final[list[str]] = [
        "icontains",
        "contains",
        "exact",
        "iexact",
        "startswith",
        "istartswith",
        "endswith",
        "iendswith",
        "regex",
        "iregex",
        "in"
    ]
    """Standard filter options for text fields."""

    DATETIME: Final[list[str]] = [
        "date",
        "date__gte",
        "date__lte",
        "date__gt",
        "date__lt",
        "date__in",
        "date__range",
        "time",
        "time__gte",
        "time__lte",
        "time__gt",
        "time__lt",
        "time__in",
        "time__range",
        "iso_year",
        "iso_year",
        "iso_year__gte",
        "iso_year__lte",
        "iso_year__gt",
        "iso_year__lt",
        "iso_year__in",
        "iso_year__range",
        "month",
        "month__gte",
        "month__lte",
        "month__gt",
        "month__lt",
        "month__in",
        "month__range",
        "quarter",
        "quarter__gte",
        "quarter__lte",
        "quarter__gt",
        "quarter__lt",
        "quarter__in",
        "quarter__range",
        "week",
        "week__gte",
        "week__lte",
        "week__gt",
        "week__lt",
        "week__in",
        "week__range",
        "iso_week_day",
        "iso_week_day__gte",
        "iso_week_day__lte",
        "iso_week_day__gt",
        "iso_week_day__lt",
        "iso_week_day__in",
        "iso_week_day__range",
        "day",
        "day__gte",
        "day__lte",
        "day__gt",
        "day__lt",
        "day__in",
        "day__range",
        "hour",
        "hour__gte",
        "hour__lte",
        "hour__gt",
        "hour__lt",
        "hour__in",
        "hour__range",
        "minute",
        "minute__gte",
        "minute__lte",
        "minute__gt",
        "minute__lt",
        "minute__in",
        "minute__range",
        "second",
        "second__gte",
        "second__lte",
        "second__gt",
        "second__lt",
        "second__in",
        "second__range",
    ]

    FLOAT: Final[list[str]] = [
        "lte",
        "gte",
        "range"
    ]
    """Standard filter options for float fields."""


    INT: Final[list[str]] = [
        "lte",
        "gte",
        "lt",
        "gt",
        "exact",
        "in",
        "range"
    ]
    """Standard filter options for integer fields."""


    BOOL: Final[list[str]] = ["exact"]
    """Standard filter options for boolean fields."""


    CHOICE: Final[list[str]] = [
        "icontains",
        "iexact",
        "in"
    ]
    """Standard filter options for fields with constant choices."""



# Configurations

class EMailArchiverDaemonConfiguration:
    """Namespace class for all configurations constants for the :class:`Emailkasten.EMailArchiverDaemon` instances."""

    CYCLE_PERIOD_DEFAULT: Final[int] = 60
    """The default cycle period of the daemons in seconds."""

    RESTART_TIME: Final[int] = 10
    """The default restart time for the daemons in case of a crash in seconds."""


class StorageConfiguration:
    """Namespace class for all configurations constants for the :class:`Emailkasten.Models.StorageModel`."""

    MAX_SUBDIRS_PER_DIR: Final[int] = 1000
    """The maximum numbers of subdirectories in one storage unit. Must not exceed 64000 for ext4 filesystem! """

    STORAGE_PATH: Final[str] = "/mnt/archive"
    """The path to the storage for the saved data. Must match the path in the docker-compose.yml to ensure data safety."""

    PRERENDER_IMAGETYPE: Final[str] = "jpg"
    """The image format for the prerendered eml files."""


class LoggerConfiguration:
    """Namespace class for all configurations constants for the application loggers."""

    LOG_DIRECTORY_PATH: Final[str] = ""  # /var/log
    """The path to directory with the logs.
    Must match the path in the docker-compose.yml to store the logs outside the container."""

    APP_LOGFILE_NAME: Final[str] = "Emailkasten.log"
    """The name of the Emailkasten logfile."""

    DJANGO_LOGFILE_NAME: Final[str] = "django.log"
    """The name of the django logfile."""

    APP_LOG_LEVEL: Final[str] = os.environ.get("APP_LOG_LEVEL", "INFO")
    """The loglevel to the Emailkasten logfile.
    Is being set from an environment variable of the same name.
    Defaults to INFO."""

    DJANGO_LOG_LEVEL: Final[str] = os.environ.get("DJANGO_LOG_LEVEL", "INFO")
    """The loglevel to the django logfile.
    Is being set from an environment variable of the same name.
    Defaults to INFO."""

    ROOT_LOG_LEVEL: Final[str] = os.environ.get("ROOT_LOG_LEVEL", "INFO")
    """The loglevel to the root console logger.
    Is being set from an environment variable of the same name.
    Defaults to INFO."""

    LOGFILE_MAXSIZE: Final[int] = int(
        os.environ.get("LOGFILE_MAXSIZE", 10 * 1024 * 1024)
    )
    """The maximum file size of a logfile.
    Is being set from an environment variable of the same name.
    Defaults to 10 MB.

    Todo:
        The int cast it not safe!"""

    LOGFILE_BACKUP_NUMBER: Final[int] = int(os.environ.get("LOGFILE_BACKUP_NUMBER", 5))
    """The maximum number of backup logfiles to keep.
    Is being set from an environment variable of the same name.
    Defaults to 5.

    Todo:
        The int cast is not safe!"""

    LOG_FORMAT: Final[str] = "{asctime} {levelname} - {name}.{funcName}: {message}"
    """The format of the log messages for all loggers."""


class ParsingConfiguration:
    """Namespace class for all configurations constants for the parsing of mails."""

    CHARSET_DEFAULT: Final[str] = "utf-8"
    """The default charset used for parsing of text."""

    STRIP_TEXTS: Final[bool] = True
    """Whether or not to strip whitespace from textfields like bodytext and subject."""

    THROW_OUT_SPAM: Final[bool] = True
    """Whether or not to ignore emails that have a spam flag."""

    APPLICATION_TYPES: Final[list[str]] = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]
    """A list of application types to parse as attachments."""

    DATE_DEFAULT: Final[str] = "1971-01-01 00:00:00"
    """The fallback date to use if none is found in a mail."""

    DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"
    """The mail datetime format as specified in RFC5322. Must match the pattern of :attr:`DATE_DEFAULT`."""


class ProcessingConfiguration:
    """Namespace class for all configurations constants for the processing, especially the prerendering, of mails."""

    DUMP_DIRECTORY: Final[str] = "/tmp/images"
    """The directory path where temporary images of the prerendering process will be placed."""

    HTML_FORMAT: Final[
        str
    ] = """
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    font-size: 14px;
                    white-space: pre-wrap;
                }}
            </style>
        </head>
        <body>
            <pre>%s</pre>
        </body>
        </html>
        """
    """The html template to wrap around plain text before prerendering."""


class FetchingConfiguration:
    """Namespace class for all configurations constants for the fetching of mails."""

    SAVE_TO_EML_DEFAULT: Final[bool] = True
    """The default setting whether to store mails as eml. Initially set to True."""

    SAVE_ATTACHMENTS_DEFAULT: Final[bool] = True
    """The default setting whether to store attachments. Initially set to True."""

    SAVE_IMAGES_DEFAULT: Final[bool] = True
    """The default setting whether to store images. Initially set to True."""


class DatabaseConfiguration:
    """Namespace class for all configurations constants for the database."""

    NAME: Final[str] = os.environ.get("DB_NAME", "emailkasten")
    """The name of the database on the mariadb server. Can be set from docker-compose.yml."""

    USER: Final[str] = os.environ.get("DB_USER", "user")
    """The name of the database user. Can be set from docker-compose.yml."""

    PASSWORD: Final[str] = os.environ.get("DB_PASSWORD", "passwd")
    """The password of the database user. Can be set from docker-compose.yml."""

    RECONNECT_RETRIES: Final[int] = 10
    """The number of reconnect attempt in case of database disconnect."""

    RECONNECT_DELAY: Final[int] = 30
    """The delay between reconnect attempt in case of database disconnect."""


class APIConfiguration:
    """Namespace class for all configuration constants of the API."""

    DEFAULT_PAGE_SIZE: Final[int] = 20
    """The default number of entries per paginated response."""

    MAX_PAGE_SIZE: Final[int] = 200
    """The maximal number of entries per paginated response."""

    REGISTRATION_ENABLED: Final[bool] = os.environ.get("REGISTRATION_ENABLED", False)
    """Whether reegistration of new users is enabled."""


class ParsedMailKeys:
    """Namespace class for all keys to the parsedMail dictionary."""

    DATA: Final[str] = "Raw"
    FULL_MESSAGE: Final[str] = "Full"
    SIZE: Final[str] = "Size"
    EML_FILE_PATH: Final[str] = "EmlFilePath"
    PRERENDER_FILE_PATH: Final[str] = "PrerenderFilePath"
    ATTACHMENTS: Final[str] = "Attachments"
    IMAGES: Final[str] = "Images"
    MAILINGLIST: Final[str] = "Mailinglist"
    BODYTEXT: Final[str] = "Bodytext"

    class Header:
        """For existing header fields see https://www.iana.org/assignments/message-headers/message-headers.xhtml."""

        MESSAGE_ID: Final[str] = "Message-ID"
        IN_REPLY_TO: Final[str] = "In-Reply-To"

        DATE: Final[str] = "Date"
        SUBJECT: Final[str] = "Subject"
        COMMENTS: Final[str] = "Comments"
        KEYWORDS: Final[str] = "Keywords"

        RECEIVED: Final[str] = "Received"
        IMPORTANCE: Final[str] = "Importance"
        PRIORITY: Final[str] = "Priority"
        PRECEDENCE: Final[str] = "Precedence"

        LANGUAGE: Final[str] = "Language"
        CONTENT_LANGUAGE: Final[str] = "Content-Language"
        CONTENT_LOCATION: Final[str] = "Content-Location"
        CONTENT_TYPE: Final[str] = "Content-Type"

        USER_AGENT: Final[str] = "User-Agent"
        AUTO_SUBMITTED: Final[str] = "Auto-Submitted"
        ARCHIVED_AT: Final[str] = "Archived-At"

        X_PRIORITY: Final[str] = "X-Priority"
        X_ORIGINATING_CLIENT: Final[str] = "X-Originating-Client"
        X_SPAM_FLAG: Final[str] = "X-Spam-Flag"

        def __iter__(self):
            """Method to allow easier referencing of the members by listing.
            Note:
                value must come first in the listed tuples to match the format for field choices.
            """
            return iter(
                (value, attr)
                for attr, value in self.__class__.__dict__.items()
                if not attr.startswith("__")
            )

        def __getitem__(self, key):
            return getattr(self, key)


    class Correspondent:
        """Headers that are treated as correspondents."""

        FROM: Final[str] = "From"
        TO: Final[str] = "To"
        CC: Final[str] = "Cc"
        BCC: Final[str] = "Bcc"
        SENDER: Final[str] = "Sender"
        REPLY_TO: Final[str] = "Reply-To"
        RESENT_FROM: Final[str] = "Resent-From"
        RESENT_TO: Final[str] = "Resent-To"
        RESENT_CC: Final[str] = "Resent-Cc"
        RESENT_BCC: Final[str] = "Resent-Bcc"
        RESENT_SENDER: Final[str] = "Resent-Sender"
        RESENT_REPLY_TO: Final[str] = "Resent-Reply-To"
        ENVELOPE_TO: Final[str] = "Envelope-To"
        DELIVERED_TO: Final[str] = "Delivered-To"
        RETURN_PATH: Final[str] = "Return-Path"
        RETURN_RECEIPT_TO: Final[str] = "Return-Receipt-To"
        DISPOSITION_NOTIFICATION_TO: Final[str] = "Disposition-Notification-To"

        def __iter__(self):
            """Method to allow easier referencing of the members by listing.
            Note:
                value must come first in the listed tuples to match the format for field choices.
            """
            return iter(
                (value, attr)
                for attr, value in self.__class__.__dict__.items()
                if not attr.startswith("__")
            )

        def __getitem__(self, key):
            return getattr(self, key)


    class Attachment:
        """Keys to the attachment sub-dictionary."""

        DATA: Final[str] = "AttachmentData"
        SIZE: Final[str] = "AttachmentSize"
        FILE_NAME: Final[str] = "AttachmentFileName"
        FILE_PATH: Final[str] = "AttachmentFilePath"


    class Image:
        """Keys to the image sub-dictionary."""

        DATA: Final[str] = "ImageData"
        SIZE: Final[str] = "ImageSize"
        FILE_NAME: Final[str] = "ImageFileName"
        FILE_PATH: Final[str] = "ImageFilePath"


    class MailingList:
        """Keys to the mailinglist sub-dictionary."""

        ID: Final[str] = "List-Id"
        OWNER: Final[str] = "List-Owner"
        SUBSCRIBE: Final[str] = "List-Subscribe"
        UNSUBSCRIBE: Final[str] = "List-Unsubscribe"
        POST: Final[str] = "List-Post"
        HELP: Final[str] = "List-Help"
        ARCHIVE: Final[str] = "List-Archive"
