# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os

class MailFetchingCriteria:
    """Namespace class for all implemented mail fetching criteria constants.
    For a list of all existing IMAP criteria see https://datatracker.ietf.org/doc/html/rfc3501.html#section-6.4.4
    Note that IMAP does not support time just dates. So we are always refering to full days.
    POP does not support queries at all, so everything will be fetched."""

    RECENT = "RECENT"
    """Filter by "RECENT" flag."""

    UNSEEN = "UNSEEN"
    """Filter by "UNSEEN" flag."""

    ALL = "ALL"
    """Filter by "ALL" flag."""

    NEW = "NEW"
    """Filter by "NEW" flag."""

    OLD = "OLD"
    """Filter by "OLD" flag."""

    FLAGGED = "FLAGGED"
    """Filter by "FLAGGED" flag."""

    ANSWERED = "ANSWERED"
    """Filter by "ANSWERED" flag."""

    DAILY = "DAILY"
    """Filter using "SENTSINCE" for mails sent the previous day or later."""

    WEEKLY = "WEEKLY"
    """Filter using "SENTSINCE" for mails sent the previous week (counting back from now) or later."""

    MONTHLY = "MONTHLY"
    """Filter using "SENTSINCE" for mails sent the previous 4 weeks (counting back from now) or later."""

    ANNUALLY = "ANNUALLY"
    """Filter using "SENTSINCE" for mails sent the previous 52 weeks (counting back from now) or later."""


    def __iter__(self):
        """Method to allow easier referencing of the members by listing."""
        return iter((attr, value) for attr, value in self.__class__.__dict__.items() if not attr.startswith("__"))

    def __getitem__(self, key):
        return getattr(self, key)



class MailFetchingProtocols:
    """Namespace class for all implemented mail protocols constants."""

    IMAP = "IMAP"
    """The IMAP4 protocol."""
    
    IMAP_SSL = "IMAP_SSL"
    """The IMAP4 protocol over SSL."""
    
    POP3 = "POP3"
    """The POP3 protocol."""
    
    POP3_SSL = "POP3_SSL"
    """The POP3 protocol over SSL."""
    
    EXCHANGE = "EXCHANGE"
    """Microsofts Exchange protocol."""



class EMailArchiverDaemonConfiguration:
    """Namespace class for all configurations constants for the :class:`Emailkasten.EMailArchiverDaemon` instances."""

    CYCLE_PERIOD_DEFAULT = 60
    """The default cycle period of the daemons in seconds."""

    RESTART_TIME = 10
    """The default restart time for the daemons in case of a crash in seconds."""



class StorageConfiguration:
    """Namespace class for all configurations constants for the :class:`Emailkasten.Models.StorageModel`."""
    
    MAX_SUBDIRS_PER_DIR = 1000
    """The maximum numbers of subdirectories in one storage unit. Must not exceed 64000 for ext4 filesystem! """
    
    STORAGE_PATH = "/mnt/archive"
    """The path to the storage for the saved data. Must match the path in the docker-compose.yml to ensure data safety."""
    
    PRERENDER_IMAGETYPE = 'jpg'
    """The image format for the prerendered eml files."""



class LoggerConfiguration:
    """Namespace class for all configurations constants for the application loggers."""
   
    APP_LOGFILE_PATH = "Emailkasten.log" # /var/log/
    """The path to the Emailkasten logfile."""

    DJANGO_LOGFILE_PATH = "django.log"  # /var/log/
    """The path to the django logfile."""

    APP_LOG_LEVEL = os.environ.get('APP_LOG_LEVEL', 'INFO')
    """The loglevel to the Emailkasten logfile. Is being set from an environment variable of the same name."""
    
    DJANGO_LOG_LEVEL = os.environ.get('DJANGO_LOG_LEVEL', 'INFO')
    """The loglevel to the django logfile. Is being set from an environment variable of the same name."""
    
    ROOT_LOG_LEVEL = os.environ.get('ROOT_LOG_LEVEL', 'INFO')
    """The loglevel to the root console logger. Is being set from an environment variable of the same name."""
    
    LOGFILE_MAXSIZE = 10 * 1024 * 1024 # 10 MiB
    """The maximum file size of a logfile."""
    
    LOGFILE_BACKUP_NUMBER = 3 
    """The maximum number of backup logfiles to keep."""
    
    LOG_FORMAT = '{asctime} {levelname} - {name}.{funcName}: {message}'
    """The format of the log messages for all loggers."""



class ParsingConfiguration:
    """Namespace class for all configurations constants for the parsing of mails."""

    CHARSET_DEFAULT = 'utf-8'
    """The default charset used for parsing of text."""
    
    STRIP_TEXTS = True
    """Whether or not to strip whitespace from textfields like bodytext and subject."""
    
    THROW_OUT_SPAM = True
    """Whether or not to ignore emails that have a spam flag."""
    
    APPLICATION_TYPES = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    """A list of application types to parse as attachments."""
    
    DATE_DEFAULT = "1971-01-01 00:00:00"
    """The fallback date to use if none is found in a mail."""
    
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    """The mail datetime format as specified in RFC5322. Must match the pattern of `DATE_DEFAULT`."""


    
class ProcessingConfiguration:
    """Namespace class for all configurations constants for the processing, especially the prerendering, of mails."""

    DUMP_DIRECTORY = '/tmp/images'
    """The directory path where temporary images of the prerendering process will be placed."""

    HTML_FORMAT = """
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

    SAVE_TO_EML_DEFAULT = True
    """The default setting whether to store mails as eml. Initially set to True."""
    
    SAVE_ATTACHMENTS_DEFAULT = True
    """The default setting whether to store attachments. Initially set to True."""
    
    SAVE_IMAGES_DEFAULT = True
    """The default setting whether to store images. Initially set to True."""
    


class DatabaseConfiguration:
    """Namespace class for all configurations constants for the database."""

    NAME = os.environ.get("DB_NAME", "emailkasten")
    """The name of the database on the mariadb server. Can be set from docker-compose.yml."""
    
    USER = os.environ.get("DB_USER", "user")
    """The name of the database user. Can be set from docker-compose.yml."""
    
    PASSWORD = os.environ.get("DB_PASSWORD", "passwd")
    """The password of the database user. Can be set from docker-compose.yml."""

    RECONNECT_RETRIES = 10
    """The number of reconnect attempt in case of database disconnect."""

    RECONNECT_DELAY = 30
    """The delay between reconnect attempt in case of database disconnect."""



class ParsedMailKeys:
    #Keys to the dict
    DATA = "Raw"
    FULL_MESSAGE = "Full"
    SIZE = "Size"
    EML_FILE_PATH = "EmlFilePath"
    PRERENDER_FILE_PATH = "PrerenderFilePath"
    ATTACHMENTS = "Attachments"
    IMAGES = "Images"
    MAILINGLIST = "Mailinglist"
    BODYTEXT = "Bodytext"
    
    class Header:
        """For existing header fields see https://www.iana.org/assignments/message-headers/message-headers.xhtml."""
        MESSAGE_ID = "Message-ID"
        IN_REPLY_TO = "In-Reply-To"
        
        DATE = "Date"
        SUBJECT = "Subject"
        COMMENTS = "Comments"
        KEYWORDS = "Keywords"
    
        RECEIVED = "Received"
        IMPORTANCE = "Importance"
        PRIORITY = "Priority"
        PRECEDENCE = "Precedence"

        LANGUAGE = "Language"
        CONTENT_LANGUAGE = "Content-Language"
        CONTENT_LOCATION = "Content-Location"
        CONTENT_TYPE = "Content-Type"

        USER_AGENT = "User-Agent"
        AUTO_SUBMITTED = "Auto-Submitted"
        ARCHIVED_AT = "Archived-At"

        X_PRIORITY = "X-Priority"
        X_ORIGINATING_CLIENT = "X-Originating-Client"
        X_SPAM_FLAG = "X-Spam-Flag"
        
        
    class Correspondent:
        FROM = "From"
        TO = "To"
        CC = "Cc"
        BCC = "Bcc"
        SENDER = "Sender"
        REPLY_TO = "Reply-To"
        RESENT_FROM = "Resent-From"
        RESENT_TO = "Resent-To"
        RESENT_CC = "Resent-Cc"
        RESENT_BCC = "Resent-Bcc"
        RESENT_SENDER = "Resent-Sender"
        RESENT_REPLY_TO = "Resent-Reply-To"
        ENVELOPE_TO = "Envelope-To"
        DELIVERED_TO = "Delivered-To"
        RETURN_PATH = "Return-Path"
        RETURN_RECEIPT_TO = "Return-Receipt-To"
        DISPOSITION_NOTIFICATION_TO = "Disposition-Notification-To"
        
        def __iter__(self):
            return iter((attr, value) for attr, value in self.__class__.__dict__.items() if not attr.startswith("__"))

        def __getitem__(self, key):
            return getattr(self, key)
            

    #attachment keys
    class Attachment:
        DATA = "AttachmentData"
        SIZE= "AttachmentSize"
        FILE_NAME = "AttachmentFileName"
        FILE_PATH= "AttachmentFilePath" 
    
    #image keys
    class Image:
        DATA = "ImageData"
        SIZE= "ImageSize"
        FILE_NAME = "ImageFileName"
        FILE_PATH= "ImageFilePath" 
    
    #mailinglist keys
    class MailingList:
        ID = "List-Id"
        OWNER = "List-Owner"
        SUBSCRIBE = "List-Subscribe"
        UNSUBSCRIBE = "List-Unsubscribe"
        POST = "List-Post"
        HELP = "List-Help"
        ARCHIVE = "List-Archive"