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

class LoggerConfiguration:
    LOGGER_NAME = "EMailkasten"
    LOGFILE_PATH = f"/var/log/{LOGGER_NAME}.log" 
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOGFILE_MAXSIZE = 10 * 1024 * 1024 # 10 MB
    LOGFILE_BACKUP_NUMBER = 3 
    CONSOLE_LOGGING = False
    LOG_FORMAT = '{name} {levelname} {asctime} {module} {message}'

class ParsingConfiguration:
    CHARSET_DEFAULT = 'utf-8'
    STRIP_TEXTS = True
    
class FetchingConfiguration:
    SAVE_TO_EML_DEFAULT = True
    SAVE_ATTACHMENTS_DEFAULT = True
    
class DatabaseConfiguration:
    NAME = os.environ.get("DB_NAME", "emailkasten")
    USER = os.environ.get("DB_USER", "user")
    PASSWORD = os.environ.get("DB_PASSWORD", "passwd")
