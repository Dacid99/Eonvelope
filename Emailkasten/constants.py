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
    RECENT = "RECENT"
    UNSEEN = "UNSEEN"
    ALL = "ALL"
    NEW = "NEW"
    DAILY = "DAILY"

class MailFetchingProtocols:
    IMAP = "IMAP"
    IMAP_SSL = "IMAP_SSL"
    POP3 = "POP3"
    POP3_SSL = "POP3_SSL"
    EXCHANGE = "EXCHANGE"

class EMailArchiverDaemonConfiguration:
    CYCLE_PERIOD_DEFAULT = 60
    RESTART_TIME = 10

class StorageConfiguration:
    MAX_SUBDIRS_PER_DIR = 1000
    STORAGE_PATH = "/mnt/archive"
    PRERENDER_IMAGETYPE = 'jpg'

class LoggerConfiguration:
    APP_LOGFILE_PATH = "/var/log/Emailkasten.log" # 
    DJANGO_LOGFILE_PATH = "/var/log/django.log"  # 
    APP_LOG_LEVEL = os.environ.get('APP_LOG_LEVEL', 'INFO')
    DJANGO_LOG_LEVEL = os.environ.get('DJANGO_LOG_LEVEL', 'INFO')
    ROOT_LOG_LEVEL = os.environ.get('ROOT_LOG_LEVEL', 'INFO')
    LOGFILE_MAXSIZE = 10 * 1024 * 1024 # 10 MB
    LOGFILE_BACKUP_NUMBER = 3 
    LOG_FORMAT = '{asctime} {levelname} - {name}.{funcName}: {message}'

class ParsingConfiguration:
    CHARSET_DEFAULT = 'utf-8'
    STRIP_TEXTS = True
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