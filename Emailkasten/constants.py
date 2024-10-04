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

class MENTIONS:
    FROM = "FROM"
    TO = "TO"
    CC = "CC"
    BCC = "BCC"

class EMailArchiverDaemonConfiguration:
    CYCLE_PERIOD_DEFAULT = 60
    RESTART_TIME = 10

class StorageConfiguration:
    MAX_SUBDIRS_PER_DIR = 10000
    STORAGE_PATH = "/mnt/archive"
    PRERENDER_IMAGETYPE = 'jpg'

class LoggerConfiguration:
    LOGGER_NAME = "EMailkasten"
    LOGFILE_PATH = f"/var/log/{LOGGER_NAME}.log"  #"helperlog.log"
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOGFILE_MAXSIZE = 10 * 1024 * 1024 # 10 MB
    LOGFILE_BACKUP_NUMBER = 3 
    CONSOLE_LOGGING = False
    LOG_FORMAT = '{name} {levelname} {asctime} {module} {message}'

class ParsingConfiguration:
    CHARSET_DEFAULT = 'utf-8'
    STRIP_TEXTS = True
    
class ProcessingConfiguration:
    DUMP_DIRECTORY = '/tmp/images'
    
class FetchingConfiguration:
    SAVE_TO_EML_DEFAULT = True
    SAVE_ATTACHMENTS_DEFAULT = True
    
class DatabaseConfiguration:
    NAME = os.environ.get("DB_NAME", "emailkasten")
    USER = os.environ.get("DB_USER", "user")
    PASSWORD = os.environ.get("DB_PASSWORD", "passwd")
