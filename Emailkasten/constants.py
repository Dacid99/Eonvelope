'''
    Emailkasten - a open-source self-hostable email archiving server
    Copyright (C) 2024  David & Philipp Aderbauer

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

import os

class MailFetchingCriteria:
    """Namespace class for all implemented mail fetching criteria constants.
    Note that IMAP does not support time just dates. So we are always refering to full days.
    
    Attributes:
        RECENT (str): Filter by "RECENT" flag.
        UNSEEN (str): Filter by "UNSEEN" flag.
        ALL (str): Filter by "ALL" flag.
        NEW (str): Filter by "NEW" flag.
        OLD (str): Filter by "OLD" flag.
        FLAGGED (str): Filter by "FLAGGED" flag.
        ANSWERED (str): Filter by "ANSWERED" flag.
        DAILY (str): Filter using "SENTSINCE" for mails sent the previous day or later.
        WEEKLY (str): Filter using "SENTSINCE" for mails sent the previous week (counting back from now) or later.
        MONTHLY (str): Filter using "SENTSINCE" for mails sent the previous 4 weeks (counting back from now) or later.
        ANNUALLY (str): Filter using "SENTSINCE" for mails sent the previous 52 weeks (counting back from now) or later.
    """
    RECENT = "RECENT"
    UNSEEN = "UNSEEN"
    ALL = "ALL"
    NEW = "NEW"
    OLD = "OLD"
    FLAGGED = "FLAGGED"
    ANSWERED = "ANSWERED"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    ANNUALLY = "ANNUALLY"

    def __iter__(self):
        """Method to allow easier referencing of the members by listing"""
        return iter((attr, value) for attr, value in self.__class__.__dict__.items() if not attr.startswith("__"))

    def __getitem__(self, key):
        return getattr(self, key)


class MailFetchingProtocols:
    """Namespace class for all implemented mail protocols constants.
    
    Attributes:
        IMAP (str): The IMAP4 protocol.
        IMAP_SSL (str): The IMAP4 protocol over SSL.
        POP3 (str): The POP3 protocol.
        POP3_SSL (str): The POP3 protocol over SSL.
        EXCHANGE (str): Microsofts Exchange protocol.
    """
    IMAP = "IMAP"
    IMAP_SSL = "IMAP_SSL"
    POP3 = "POP3"
    POP3_SSL = "POP3_SSL"
    EXCHANGE = "EXCHANGE"

class EMailArchiverDaemonConfiguration:
    """Namespace class for all configurations constants for the :class:`Emailkasten.EMailArchiverDaemon` instances.
    
    Attributes:
        CYCLE_PERIOD_DEFAULT (int): The default cycle period of the daemons, in seconds, initially set to 60.
        RESTART_TIME (int): The default restart time for the daemons in case of a crash, in seconds, initially set to 10.
    """
    CYCLE_PERIOD_DEFAULT = 60
    RESTART_TIME = 10

class StorageConfiguration:
    """Namespace class for all configurations constants for the :class:`Emailkasten.Models.StorageModel`.
    
    Attributes:
        MAX_SUBDIRS_PER_DIR (int): The maximum numbers of subdirectories in one storage unit. Initially set to 1000. Must not exceed 64000 for ext4 filesystem! 
        STORAGE_PATH (str): The path to the storage for the saved data. Intially set to /mnt/archive. Must match the path in the docker-compose.yml to ensure data safety.
        PRERENDER_IMAGETYPE (str): The image format for the prerendered eml files. Initially set to jpg.
    """
    MAX_SUBDIRS_PER_DIR = 1000
    STORAGE_PATH = "/mnt/archive"
    PRERENDER_IMAGETYPE = 'jpg'

class LoggerConfiguration:
    """Namespace class for all configurations constants for the application loggers.
    
    Attributes:
        APP_LOGFILE_PATH (str): The path to the Emailkasten logfile. Initially set to /var/log/Emailkasten.log . 
        DJANGO_LOGFILE_PATH (str):  The path to the django logfile. Initially set to /var/log/django.log . 
        APP_LOG_LEVEL (str):  The loglevel to the Emailkasten logfile. Is being set from an environment variable of the same name. Defaults to INFO. 
        DJANGO_LOG_LEVEL (str): The loglevel to the django logfile. Is being set from an environment variable of the same name. Defaults to INFO. 
        ROOT_LOG_LEVEL (str): The loglevel to the root console logger. Is being set from an environment variable of the same name. Defaults to INFO. 
        LOGFILE_MAXSIZE (int): The maximum file size of a logfile. Initially set to 10 MiB.
        LOGFILE_BACKUP_NUMBER (int): The maximum number of backup logfiles to keep. Initially set to 3.
        LOG_FORMAT (str): The format of the log messages for all loggers. Initially set to '{asctime} {levelname} - {name}.{funcName}: {message}'.
    """
    APP_LOGFILE_PATH = "Emailkasten.log" # /var/log/
    DJANGO_LOGFILE_PATH = "django.log"  # /var/log/
    APP_LOG_LEVEL = os.environ.get('APP_LOG_LEVEL', 'INFO')
    DJANGO_LOG_LEVEL = os.environ.get('DJANGO_LOG_LEVEL', 'INFO')
    ROOT_LOG_LEVEL = os.environ.get('ROOT_LOG_LEVEL', 'INFO')
    LOGFILE_MAXSIZE = 10 * 1024 * 1024 # 10 MiB
    LOGFILE_BACKUP_NUMBER = 3 
    LOG_FORMAT = '{asctime} {levelname} - {name}.{funcName}: {message}'

class ParsingConfiguration:
    """Namespace class for all configurations constants for the parsing of mails.
    
    Attributes:
        CHARSET_DEFAULT (str): The default charset used for parsing of text. Initially set to utf-8.
        STRIP_TEXTS (bool): Whether or not to strip whitespace from textfields like bodytext and subject. Initially set to True.
        THROW_OUT_SPAM (bool): Whether or not to ignore emails that have a spam flag. Initially set to True.
        APPLICATION_TYPES (list): A list of application types to parse as attachments. Initially set to ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    """
    CHARSET_DEFAULT = 'utf-8'
    STRIP_TEXTS = True
    THROW_OUT_SPAM = True
    APPLICATION_TYPES = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    
class ProcessingConfiguration:
    DUMP_DIRECTORY = '/tmp/images'
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
    
class FetchingConfiguration:
    SAVE_TO_EML_DEFAULT = True
    SAVE_ATTACHMENTS_DEFAULT = True
    SAVE_IMAGES_DEFAULT = True
    
class DatabaseConfiguration:
    NAME = os.environ.get("DB_NAME", "emailkasten")
    USER = os.environ.get("DB_USER", "user")
    PASSWORD = os.environ.get("DB_PASSWORD", "passwd")
    RECONNECT_RETRIES = 10
    RECONNECT_DELAY = 30

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
        BCC = "Bcc"
        CC = "Cc"
        REPLY_TO = "Reply-To"
        RETURN_PATH = "Return-Path"
        ENVELOPE_TO = "Envelope-To"
        DELIVERED_TO = "Delivered-To"
        SENDER = "Sender"
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