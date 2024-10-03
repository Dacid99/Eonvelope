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

from .Fetchers.IMAP_SSL_Fetcher import IMAP_SSL_Fetcher
from .Fetchers.IMAPFetcher import IMAPFetcher
from .Fetchers.POP3_SSL_Fetcher import POP3_SSL_Fetcher
from .Fetchers.POP3Fetcher import POP3Fetcher
from .Fetchers.ExchangeFetcher import ExchangeFetcher
from .FileManager import FileManager
from .LoggerFactory import LoggerFactory
from .MailParser import MailParser
from .EMailDBFeeder import EMailDBFeeder
import datetime
import email
import email.header
import imgkit
import os
import quopri
import base64
import hashlib
from PIL import Image
from . import constants

class MailProcessor:

    @staticmethod
    def getFilter(flag):
        if flag == constants.MailFetchingCriteria.DAILY:
            return "SINCE {date}".format(date=datetime.date.today().strftime("%d-%b-%Y"))
        else: 
            return flag
        
    @staticmethod
    def test(account):
        logger = LoggerFactory.getChildLogger(MailProcessor.__name__)

        logger.debug(f"Testing {str(account)} ...")
        if account.protocol == IMAPFetcher.PROTOCOL:
                result = IMAPFetcher.test(account)

        elif account.protocol == IMAP_SSL_Fetcher.PROTOCOL:
                result = IMAP_SSL_Fetcher.test(account)

        elif account.protocol == POP3Fetcher.PROTOCOL:
                result = POP3Fetcher.test(account)

        elif account.protocol == POP3_SSL_Fetcher.PROTOCOL:
                result = POP3_SSL_Fetcher.test(account)

        elif account.protocol == ExchangeFetcher.PROTOCOL:
                result = ExchangeFetcher.test(account)

        else:
            logger.error("Can not fetch mails, protocol is not or incorrectly specified!")
            result = False

        logger.debug(f"Tested {str(account)} as {result}")
        return result


    @staticmethod
    def scanMailboxes(mailAccount):
        logger = LoggerFactory.getChildLogger(MailProcessor.__name__)

        logger.debug(f"Searching mailboxes in {mailAccount}...")

        if mailAccount.protocol == IMAPFetcher.PROTOCOL:
            with IMAPFetcher(mailAccount) as imapMail:

                mailboxes = imapMail.fetchMailboxes()

        elif mailAccount.protocol == IMAP_SSL_Fetcher.PROTOCOL:
            with IMAP_SSL_Fetcher(mailAccount) as imapMail:

                mailboxes = imapMail.fetchMailboxes()

        elif mailAccount.protocol == POP3Fetcher.PROTOCOL:
            mailboxes = ['INBOX']

        elif mailAccount.protocol == POP3_SSL_Fetcher.PROTOCOL:
            mailboxes = ['INBOX']

        elif mailAccount.protocol == ExchangeFetcher.PROTOCOL:
            with ExchangeFetcher(mailAccount) as exchangeMail:

                mailboxes = exchangeMail.fetchMailboxes()

        else:
            logger.error("Can not fetch mails, protocol is not or incorrectly specified!")
            mailboxes = []
            
        EMailDBFeeder.insertMailboxes(mailboxes, mailAccount)

        logger.debug("Successfully searched mailboxes")
        return mailboxes

        
    @staticmethod
    def fetch(mailbox, mailAccount, criterion):
        logger = LoggerFactory.getChildLogger(MailProcessor.__name__)

        logger.debug(f"Fetching emails with criterion {criterion} from mailbox {mailbox} in account {mailAccount}...")
        if mailAccount.protocol == IMAPFetcher.PROTOCOL:
            with IMAPFetcher(mailAccount) as imapMail:

                mailDataList = imapMail.fetchBySearch(mailbox=mailbox.name, searchCriterion=MailProcessor.getFilter(criterion))

        elif mailAccount.protocol == IMAP_SSL_Fetcher.PROTOCOL:
            with IMAP_SSL_Fetcher(mailAccount) as imapMail:

                mailDataList = imapMail.fetchBySearch(mailbox=mailbox.name, searchCriterion=MailProcessor.getFilter(criterion))

        elif mailAccount.protocol == POP3Fetcher.PROTOCOL:
            with POP3Fetcher(mailAccount) as popMail:

                mailDataList = popMail.fetchAll()

        elif mailAccount.protocol == POP3_SSL_Fetcher.PROTOCOL:
            with POP3_SSL_Fetcher(mailAccount) as popMail:

                mailDataList = popMail.fetchAll()

        elif mailAccount.protocol == ExchangeFetcher.PROTOCOL:
            with ExchangeFetcher(mailAccount) as exchangeMail:

                mailDataList = exchangeMail.fetchBySearch() #incomplete

        else:
            logger.error("Can not fetch mails, protocol is not or incorrectly specified!")
            return

        logger.debug("Successfully fetched emails")


        logger.debug("Parsing emaildata ...")
        parsedMailsList = []
        for mailData in mailDataList:
            parsedMail = MailParser.parseMail(mailData)
            parsedMailsList.append(parsedMail)
        logger.debug("Successfully parsed emaildata")


        if mailbox.save_toEML:
            logger.debug("Saving mails to eml files ...")
            for parsedMail in parsedMailsList:
                FileManager.writeMessageToEML(parsedMail)
            logger.debug("Successfully saved mails to eml files")
        else:
            logger.debug(f"Not saving to eml for mailbox {mailbox.name}")


        if mailbox.save_attachments:
            logger.debug("Saving attachments ...")
            for parsedMail in parsedMailsList:
                FileManager.writeAttachments(parsedMail)
            logger.debug("Successfully saved attachments")
        else:
            logger.debug(f"Not saving attachments for mailbox {mailbox.name}")

        logger.debug("Writing emails to database ...")
        for parsedMail in parsedMailsList:
            EMailDBFeeder.insertEMail(parsedMail, mailAccount)
        logger.debug("Successfully wrote emails to database")


    ''' 
    The following code is a modified version of code from xme's emlrender project https://github.com/xme/emlrender.
    Original code by Xavier Mertens, licensed under the GNU General Public License version 3 (GPLv3).
    Modifications by David & Philipp Aderbauer, licensed under the GNU Affero General Public License version 3 (AGPLv3).
    This modified code is part of an AGPLv3 project. See the LICENSE file for details.
    '''

    @staticmethod
    def processEml(data):
        # Create the dump directory if not existing yet
        if not os.path.isdir(dumpDir):
            os.makedirs(dumpDir)
            writeLog("[INFO] Created dump directory %s" % dumpDir)

        msg = email.message_from_bytes(data)
        try:
            decode = email.header.decode_header(msg['Date'])[0]
            dateField = str(decode[0])
        except:
            dateField = '&lt;Unknown&gt;'
        writeLog('[INFO] Date: %s' % dateField)

        try:
            decode = email.header.decode_header(msg['From'])[0]
            fromField = str(decode[0])
        except:
            fromField = '&lt;Unknown&gt;'
        writeLog('[INFO] From: %s' %  fromField)
        fromField = fromField.replace('<', '&lt;').replace('>', '&gt;')

        try:
            decode = email.header.decode_header(msg['To'])[0]
            toField = str(decode[0])
        except:
            toField = '&lt;Unknown&gt;'
        writeLog('[INFO] To: %s' % toField)
        toField = toField.replace('<', '&lt;').replace('>', '&gt;')

        try:
            decode = email.header.decode_header(msg['Subject'])[0]
            subjectField = str(decode[0])
        except:
            subjectField = '&lt;Unknown&gt;'
        writeLog('[INFO] Subject: %s' % subjectField)
        subjectField = subjectField.replace('<', '&lt;').replace('>', '&gt;')

        try:
            decode = email.header.decode_header(msg['Message-Id'])[0]
            idField = str(decode[0])
        except:
            idField = '&lt;Unknown&gt;'
        writeLog('[INFO] Message-Id: %s' % idField)
        idField = idField.replace('<', '&lt;').replace('>', '&gt;')    

        imgkitOptions = { 'load-error-handling': 'skip'}
        # imgkitOptions.update({ 'quiet': None })
        imagesList = []
        attachments = []

        # Build a first image with basic mail details
        headers = '''
        <table width="100%%">
        <tr><td align="right"><b>Date:</b></td><td>%s</td></tr>
        <tr><td align="right"><b>From:</b></td><td>%s</td></tr>
        <tr><td align="right"><b>To:</b></td><td>%s</td></tr>
        <tr><td align="right"><b>Subject:</b></td><td>%s</td></tr>
        <tr><td align="right"><b>Message-Id:</b></td><td>%s</td></tr>
        </table>
        <hr></p>
        ''' % (dateField, fromField, toField, subjectField, idField)
        m = hashlib.md5()
        m.update(headers.encode('utf-8'))
        imagePath = m.hexdigest() + '.png'
        try:
            imgkit.from_string(headers, dumpDir + '/' + imagePath, options = imgkitOptions)
            writeLog('[INFO] Created headers %s' % imagePath)
            imagesList.append(dumpDir + '/' + imagePath)
        except:
            writeLog('[WARNING] Creation of headers failed')

        #
        # Main loop - process the MIME parts
        #
        for part in msg.walk():
            mimeType = part.get_content_type()
            if part.is_multipart():
                writeLog('[INFO] Multipart found, continue')
                continue

            writeLog('[INFO] Found MIME part: %s' % mimeType)
            if mimeType in textTypes:
                try:
                    payload = quopri.decodestring(part.get_payload(decode=True)).decode('utf-8')
                except:
                    payload = str(quopri.decodestring(part.get_payload(decode=True)))[2:-1]
                
                # Cleanup dirty characters
                dirtyChars = [ '\n', '\\n', '\t', '\\t', '\r', '\\r']
                for char in dirtyChars:
                    payload = payload.replace(char, '')
                
                # Generate MD5 hash of the payload
                m = hashlib.md5()
                m.update(payload.encode('utf-8'))
                imagePath = m.hexdigest() + '.png'
                try:
                    imgkit.from_string(payload, dumpDir + '/' + imagePath, options = imgkitOptions)
                    writeLog('[INFO] Decoded %s' % imagePath)
                    imagesList.append(dumpDir + '/' + imagePath)
                except:
                    writeLog('[WARNING] Decoding this MIME part returned error')
            elif mimeType in imageTypes:
                payload = part.get_payload(decode=False)
                imgdata = base64.b64decode(payload)
                # Generate MD5 hash of the payload
                m = hashlib.md5()
                m.update(payload.encode('utf-8'))
                imagePath = m.hexdigest() + '.' + mimeType.split('/')[1]
                try:
                    with open(dumpDir + '/' + imagePath, 'wb') as f:
                        f.write(imgdata)
                    writeLog('[INFO] Decoded %s' % imagePath)
                    imagesList.append(dumpDir + '/' + imagePath)
                except:
                    writeLog('[WARNING] Decoding this MIME part returned error')
            else:
                fileName = part.get_filename()
                if not fileName:
                    fileName = "Unknown"
                attachments.append("%s (%s)" % (fileName, mimeType))
                writeLog('[INFO] Skipped attachment %s (%s)' % (fileName, mimeType))

        if len(attachments):
            footer = '<p><hr><p><b>Attached Files:</b><p><ul>'
            for a in attachments:
                footer = footer + '<li>' + a + '</li>'
            footer = footer + '</ul><p><br>Generated by EMLRender v1.0'
            m = hashlib.md5()
            m.update(footer.encode('utf-8'))
            imagePath = m.hexdigest() + '.png'
            try:
                imgkit.from_string(footer, dumpDir + '/' + imagePath, options = imgkitOptions)
                writeLog('[INFO] Created footer %s' % imagePath)
                imagesList.append(dumpDir + '/' + imagePath)
            except:
                writeLog('[WARNING] Creation of footer failed')

        resultImage = dumpDir + '/' + 'new.png'
        if len(imagesList) > 0:
            images = list(map(Image.open, imagesList))
            combo = appendImages(images)
            combo.save(resultImage)
            # Clean up temporary images
            for i in imagesList:
            os.remove(i)
            return(resultImage)
        else:
            return(False)