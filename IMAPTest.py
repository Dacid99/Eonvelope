from Emailkasten.Fetchers.IMAP_SSL_Fetcher import IMAP_SSL_Fetcher
from Emailkasten.MailParser import MailParser
from Emailkasten.MailProcessor import MailProcessor
import datetime
import email.utils


with IMAP_SSL_Fetcher(username="archiv@aderbauer.org", password="nxF154j9879ZZsW", host="imap.ionos.de", port=993) as mail:

    mailsDataList = mail.fetchBySearch(mailbox='"Gesendete Objekte"', searchCriterion=MailProcessor.ALL)
    print(mailsDataList)
    
    for mailData in mailsDataList:
        parsedMail = MailParser.parseMail(mailData)
        print(parsedMail[MailParser.fullMessageString])
