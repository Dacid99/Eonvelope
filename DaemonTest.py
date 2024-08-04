import logging

from EMailArchiverDaemon import EMailArchiverDaemon


logging.basicConfig(level=logging.DEBUG)

daemon = EMailArchiverDaemon()
daemon.start()