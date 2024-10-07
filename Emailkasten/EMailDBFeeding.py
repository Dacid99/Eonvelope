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

import django.db
import logging
from .Models.EMailModel import EMailModel
from .Models.DaemonModel import DaemonModel
from .Models.MailboxModel import MailboxModel
from .Models.MailingListModel import MailingListModel 
from .Models.AttachmentModel import AttachmentModel
from .Models.ImageModel import ImageModel
from .Models.CorrespondentModel import CorrespondentModel
from .Models.EMailCorrespondentsModel import EMailCorrespondentsModel
from .MailParsing import ParsedMailKeys
from . import constants

logger = logging.getLogger(__name__)


def _insertCorrespondent(correspondentData):   
    logger.debug(f"Creating entry for correspondent in DB...")
         
    correspondentEntry, created  = CorrespondentModel.objects.get_or_create(
        email_address = correspondentData[1], 
        defaults = {'email_name': correspondentData[0]}
    )
    if created:
        logger.debug(f"Entry for {str(correspondentEntry)} created")
    else:
        logger.debug(f"Entry for {str(correspondentEntry)} already exists")
        
    return correspondentEntry
            
  
  
def _insertEMailCorrespondent(emailEntry, correspondentEntry, mention):
    logger.debug(f"Creating entry for {mention} correspondent in DB...")
    
    emailCorrespondentsEntry, created = EMailCorrespondentsModel.objects.get_or_create(
        email = emailEntry, 
        correspondent = correspondentEntry,
        mention = mention
    )
    if created:
        logger.debug(f"Entry for {str(emailCorrespondentsEntry)} created")
    else:
        logger.debug(f"Entry for {str(emailCorrespondentsEntry)} already exists")
    
   
        
def _insertAttachment(attachmentData, emailEntry):
    attachmentEntry, created  = AttachmentModel.objects.get_or_create(
        file_path = attachmentData[ParsedMailKeys.Attachment.FILE_PATH],
        email = emailEntry,
        defaults = {
            'file_name' : attachmentData[ParsedMailKeys.Attachment.FILE_NAME],
            'datasize' : attachmentData[ParsedMailKeys.Attachment.SIZE]
        }
    )
    if created:
        logger.debug(f"Entry for {str(attachmentEntry)} created")
    else:
        logger.debug(f"Entry for {str(attachmentEntry)} already exists")
     
        

def _insertImage(imageData, emailEntry):
    imageEntry, created  = ImageModel.objects.get_or_create(
        file_path = imageData[ParsedMailKeys.Image.FILE_PATH],
        email = emailEntry,
        defaults = {
            'file_name' : imageData[ParsedMailKeys.Image.FILE_NAME],
            'datasize' : imageData[ParsedMailKeys.Image.SIZE]
        }
    )
    if created:
        logger.debug(f"Entry for {str(imageEntry)} created")
    else:
        logger.debug(f"Entry for {str(imageEntry)} already exists")
        
        
        
def _insertMailinglist(mailinglistData, fromCorrespondentEntry):
    mailinglistEntry = None
    if mailinglistData[ParsedMailKeys.MailingList.ID]:
                
        logger.debug("Creating entry for mailinglist in DB...")
        mailinglistEntry, created = MailingListModel.objects.get_or_create(
                list_id = mailinglistData[ParsedMailKeys.MailingList.ID],
                defaults= {
                    'list_owner': mailinglistData[ParsedMailKeys.MailingList.OWNER],
                    'list_subscribe': mailinglistData[ParsedMailKeys.MailingList.SUBSCRIBE],
                    'list_unsubscribe': mailinglistData[ParsedMailKeys.MailingList.UNSUBSCRIBE],
                    'list_post': mailinglistData[ParsedMailKeys.MailingList.POST],
                    'list_help': mailinglistData[ParsedMailKeys.MailingList.HELP],
                    'list_archive': mailinglistData[ParsedMailKeys.MailingList.ARCHIVE],
                    'correspondent': fromCorrespondentEntry
                }
            )
        if created:
            logger.debug("Created mailinglist entry")
        else:
            logger.debug("Mailinglist entry already exists")
    else:
        logger.debug("No mailinglist ID found, not writing to DB")
        
    return mailinglistEntry
            


def insertMailbox(mailbox, account):
    try:
        with django.db.transaction.atomic():
            
            mailboxEntry, created = MailboxModel.objects.get_or_create(
                name = mailbox,
                account = account
            )
            if created:
                logger.debug(f"Entry for {str(mailboxEntry)} created")
                
                logger.debug("Attaching daemon...")
                newDaemon = DaemonModel.objects.create(mailbox = mailboxEntry)
                if not newDaemon:
                    logger.error(f"Failed to create daemon for new mailbox {mailbox}!")
                else:
                    logger.debug("Successfully created daemon for new mailbox")
            else:
                logger.debug(f"Entry for {str(mailboxEntry)} already exists")

    except django.db.IntegrityError as e:
        logger.error("Error while writing to database, rollback to last state", exc_info=True)



def insertEMail(parsedEMail, account):
    try:
        with django.db.transaction.atomic():
            
            # the FROM correspondent insertion has to be split to be able to add the FROM correspondent to an eventual mailinglist
            fromCorrespondent = parsedEMail[ParsedMailKeys.Correspondent.FROM]
            if fromCorrespondent:
                logger.debug("Adding FROM correspondent to DB...")
                
                fromCorrespondentEntry = _insertCorrespondent(fromCorrespondent[0]) #there should only be one from correspondent
            else:
                logger.error("No FROM Correspondent found in mail, not writing to DB!")
                
                
                
            mailinglistEntry = None  
            if parsedEMail[ParsedMailKeys.MAILINGLIST]:
                mailinglistEntry = _insertMailinglist(parsedEMail[ParsedMailKeys.MAILINGLIST])
            else:
                logger.debug("No mailinglist info found in mail, not writing to DB")
                
                
                
            inReplyToMailEntry = None
            if parsedEMail[ParsedMailKeys.Header.IN_REPLY_TO]:
                logger.debug("Querying inReplyTo mail ...")
                try:
                    inReplyToMailEntry = EMailModel.objects.get(message_id = parsedEMail[ParsedMailKeys.Header.IN_REPLY_TO])
                    
                    logger.debug("Successfully retrieved inReplyTo mail.")
                except EMailModel.DoesNotExist:
                    logger.warning(f"Could not find inReplyTo mail {parsedEMail[ParsedMailKeys.Header.IN_REPLY_TO]}!")     
            else:
                logger.debug("No In-Reply-To found in mail, not writing to DB")
                
            
            
            logger.debug("Creating entry for email in DB...")
            
            emailEntry, created = EMailModel.objects.get_or_create(
                message_id = parsedEMail[ParsedMailKeys.Header.MESSAGE_ID],
                defaults = {
                    'account' : account,
                    'mailinglist': mailinglistEntry,
                    'inReplyTo' : inReplyToMailEntry,
                    'bodytext' : parsedEMail[ParsedMailKeys.BODYTEXT],
                    'datasize' :  parsedEMail[ParsedMailKeys.SIZE],
                    'eml_filepath' : parsedEMail[ParsedMailKeys.EML_FILE_PATH],
                    'prerender_filepath': parsedEMail[ParsedMailKeys.PRERENDER_FILE_PATH],
                    'datetime' : parsedEMail[ParsedMailKeys.Header.DATE],
                    'email_subject' : parsedEMail[ParsedMailKeys.Header.SUBJECT],
                    'comments': parsedEMail[ParsedMailKeys.Header.COMMENTS],
                    'keywords': parsedEMail[ParsedMailKeys.Header.KEYWORDS],
                    'importance': parsedEMail[ParsedMailKeys.Header.IMPORTANCE],
                    'priority': parsedEMail[ParsedMailKeys.Header.PRIORITY],
                    'precedence': parsedEMail[ParsedMailKeys.Header.PRECEDENCE],
                    'received': parsedEMail[ParsedMailKeys.Header.RECEIVED],
                    'user_agent': parsedEMail[ParsedMailKeys.Header.USER_AGENT],
                    'auto_submitted': parsedEMail[ParsedMailKeys.Header.AUTO_SUBMITTED],
                    'content_type': parsedEMail[ParsedMailKeys.Header.CONTENT_TYPE],
                    'content_language': parsedEMail[ParsedMailKeys.Header.CONTENT_LANGUAGE],
                    'content_location': parsedEMail[ParsedMailKeys.Header.CONTENT_LOCATION],
                    'x_priority': parsedEMail[ParsedMailKeys.Header.X_PRIORITY],
                    'x_originated_client': parsedEMail[ParsedMailKeys.Header.X_ORIGINATING_CLIENT],
                    'x_spam': parsedEMail[ParsedMailKeys.Header.X_SPAM_FLAG]
                }
            )
            if created:
                logger.debug(f"Entry for {str(emailEntry)} created")
            else:
                logger.debug(f"Entry for {str(emailEntry)} already exists")
            
            
            
            if parsedEMail[ParsedMailKeys.ATTACHMENTS]: 
                logger.debug("Creating entries for attachments in DB...")
                
                for attachmentData in parsedEMail[ParsedMailKeys.ATTACHMENTS]:
                    _insertAttachment(attachmentData, emailEntry)
                
                logger.debug("Successfully added images to DB.")
            else:
                logger.debug("No attachment files found in mail, not writing to DB")
            
            
            
            if parsedEMail[ParsedMailKeys.IMAGES]: 
                logger.debug("Creating entries for images in DB...")
                
                for imageData in parsedEMail[ParsedMailKeys.IMAGES]:
                    _insertImage(imageData, emailEntry)
                    
                logger.debug("Successfully added images to DB.")
            else:
                logger.debug("No images found in mail, not writing to DB")
                
    

            for mentionType, correspondentHeader in ParsedMailKeys.Correspondent:
                if (correspondentHeader is ParsedMailKeys.Correspondent.FROM):   # from correspondent has been added earlier, just add the connection to bridge table here
                    if fromCorrespondent:
                
                        _insertEMailCorrespondent(fromCorrespondentEntry, emailEntry, mentionType)
                        
                        logger.debug(f"Successfully added entries for {mentionType} correspondent to DB.")
                    else:
                        logger.error(f"No {mentionType} correspondent found in mail, not writing to DB!")
                        
                else:
                    if parsedEMail[correspondentHeader]:
                        logger.debug(f"Creating entry for {mentionType} correspondents in DB...")
                        
                        for correspondentData in parsedEMail[correspondentHeader]:
                            correspondentEntry = _insertCorrespondent(correspondentData)
                            _insertEMailCorrespondent(emailEntry, correspondentEntry, mentionType)
                            
                        logger.debug(f"Successfully added entries for {mentionType} correspondents to DB.")
                    else:
                        logger.warning(f"No {mentionType} correspondent found in mail, not writing to DB!")


    except django.db.IntegrityError as e:
        logger.error("Error while writing to database, rollback to last state", exc_info=True)


