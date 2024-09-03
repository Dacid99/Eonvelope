from django.db import models
from rest_framework.response import Response
from .. import constants
from ..EMailArchiverDaemon import EMailArchiverDaemon 
from .MailboxModel import MailboxModel

class DaemonModel(models.Model):
    mailbox = models.OneToOneField(MailboxModel, related_name='daemon', on_delete=models.CASCADE)
    cycle_interval = models.IntegerField(default=constants.EMailArchiverDaemonConfiguration.CYCLE_PERIOD_DEFAULT)
    is_running = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'daemons'
        
    def __str__(self):
        return f"Mailfetcher daemon configuration for mailbox {self.mailbox}"
    
    
    runningDaemonsList = []
    
    def start(self):
        if not self.id in self.runningDaemonsList:
            try:
                daemon = EMailArchiverDaemon(self)
                daemon.start()
                self.runningDaemonsList[self.id] = daemon
                self.is_running = True
                self.save() 
                return Response({'status': 'Daemon started', 'account': self.mailbox.account.mail_address, 'mailbox': self.mailbox.name})
            except Exception as e:
                return Response({'status': 'Daemon failed to start!', 'account': self.mailbox.account.mail_address, 'mailbox': self.mailbox.name})
        else:
            return Response({'status': 'Daemon already running', 'account': self.mailbox.account.mail_address, 'mailbox': self.mailbox.name})
        
    
    def stop(self):
        if self.id in self.runningDaemonsList:
            daemon = self.runningDaemonsList.pop(self.id)
            daemon.stop()
            self.is_running = False
            self.save()
            return Response({'status': 'Daemon stopped', 'account': self.mailbox.account.mail_address, 'mailbox': self.mailbox.name})
        else:
            return Response({'status': 'Daemon not running', 'account': self.mailbox.account.mail_address, 'mailbox': self.mailbox.name})
        
        
