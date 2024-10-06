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
from .MailParser import MailParser
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
        file_path = attachmentData[MailParser.attachment_filePathString],
        email = emailEntry,
        defaults = {
            'file_name' : attachmentData[MailParser.attachment_fileNameString],
            'datasize' : attachmentData[MailParser.attachment_sizeString]
        }
    )
    if created:
        logger.debug(f"Entry for {str(attachmentEntry)} created")
    else:
        logger.debug(f"Entry for {str(attachmentEntry)} already exists")
     
        

def _insertImage(imageData, emailEntry):
    imageEntry, created  = ImageModel.objects.get_or_create(
        file_path = imageData[MailParser.images_filePathString],
        email = emailEntry,
        defaults = {
            'file_name' : imageData[MailParser.images_fileNameString],
            'datasize' : imageData[MailParser.images_sizeString]
        }
    )
    if created:
        logger.debug(f"Entry for {str(imageEntry)} created")
    else:
        logger.debug(f"Entry for {str(imageEntry)} already exists")
        
        
        
def _insertMailinglist(mailinglistData, fromCorrespondentEntry):
    mailinglistEntry = None
    if mailinglistData[MailParser.listIDHeader]:
                
        logger.debug("Creating entry for mailinglist in DB...")
        mailinglistEntry, created = MailingListModel.objects.get_or_create(
                list_id = mailinglistData[MailParser.listIDHeader],
                defaults= {
                    'list_owner': mailinglistData[MailParser.listOwnerHeader],
                    'list_subscribe': mailinglistData[MailParser.listSubscribeHeader],
                    'list_unsubscribe': mailinglistData[MailParser.listUnsubscribeHeader],
                    'list_post': mailinglistData[MailParser.listPostHeader],
                    'list_help': mailinglistData[MailParser.listHelpHeader],
                    'list_owner': mailinglistData[MailParser.listArchiveHeader],
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
            fromCorrespondent = parsedEMail[MailParser.fromHeader]
            if fromCorrespondent:
                logger.debug("Adding FROM correspondent to DB...")
                
                fromCorrespondentEntry = _insertCorrespondent(fromCorrespondent)
            else:
                logger.error("No FROM Correspondent found in mail, not writing to DB!")
                
                
                
            mailinglistEntry = None  
            if parsedEMail[MailParser.mailinglistString]:
                mailinglistEntry = _insertMailinglist(parsedEMail[MailParser.mailinglistString])
            else:
                logger.debug("No mailinglist info found in mail, not writing to DB")
                
                
                
            inReplyToMail = None
            if parsedEMail[MailParser.inReplyToHeader]:
                logger.debug("Querying inReplyTo mail ...")
                try:
                    inReplyToMail = EMailModel.objects.get(message_id = parsedEMail[MailParser.inReplyToHeader])
                    
                    logger.debug("Successfully retrieved inReplyTo mail.")
                except EMailModel.DoesNotExist:
                    logger.warning(f"Could not find inReplyTo mail {parsedEMail[MailParser.inReplyToHeader]}!")     
            else:
                logger.debug("No In-Reply-To found in mail, not writing to DB")
                
            
            
            logger.debug("Creating entry for email in DB...")
            
            emailEntry, created = EMailModel.objects.get_or_create(
                message_id = parsedEMail[MailParser.messageIDHeader],
                defaults = {
                    'datetime' : parsedEMail[MailParser.dateHeader],
                    'email_subject' : parsedEMail[MailParser.subjectHeader],
                    'bodytext' : parsedEMail[MailParser.bodyText],
                    'inReplyTo' : inReplyToMail,
                    'datasize' :  parsedEMail[MailParser.sizeString],
                    'eml_filepath' : parsedEMail[MailParser.emlFilePathString],
                    'prerender_filepath': parsedEMail[MailParser.prerenderFilePathString],
                    'account' : account,
                    'mailinglist': mailinglistEntry,
                    'comments': parsedEMail[MailParser.commentsHeader],
                    'keywords': parsedEMail[MailParser.keywordsHeader],
                    'importance': parsedEMail[MailParser.importanceHeader],
                    'priority': parsedEMail[MailParser.priorityHeader],
                    'precedence': parsedEMail[MailParser.precedenceHeader],
                    'received': parsedEMail[MailParser.receivedHeader],
                    'sender': parsedEMail[MailParser.senderHeader] ,
                    'return_receipt_to': parsedEMail[MailParser.returnReceiptTo] ,
                    'disposition_notification_to': parsedEMail[MailParser.dispositionNotificationTo] ,
                    'reply_to': parsedEMail[MailParser.replyToHeader] ,
                    'envelope_to': parsedEMail[MailParser.envelopeToHeader] ,
                    'delivered_to': parsedEMail[MailParser.deliveredToHeader] ,
                    'return_path': parsedEMail[MailParser.returnPathHeader] ,
                    'user_agent': parsedEMail[MailParser.userAgentHeader],
                    'auto_submitted': parsedEMail[MailParser.autoSubmittedHeader],
                    'content_type': parsedEMail[MailParser.contentTypeHeader],
                    'content_language': parsedEMail[MailParser.contentLanguageHeader],
                    'content_location': parsedEMail[MailParser.contentLocationHeader],
                    'x_priority': parsedEMail[MailParser.xPriorityHeader],
                    'x_originated_client': parsedEMail[MailParser.xOriginatingClientHeader],
                    'x_spam': parsedEMail[MailParser.xSpamFlag]                       
                }
            )
            if created:
                logger.debug(f"Entry for {str(emailEntry)} created")
            else:
                logger.debug(f"Entry for {str(emailEntry)} already exists")
            
            
            
            if parsedEMail[MailParser.attachmentsString]: 
                logger.debug("Creating entries for attachments in DB...")
                
                for attachmentData in parsedEMail[MailParser.attachmentsString]:
                    _insertAttachment(attachmentData, emailEntry)
                
                logger.debug("Successfully added images to DB.")
            else:
                logger.debug("No attachment files found in mail, not writing to DB")
            
            
            
            if parsedEMail[MailParser.imagesString]: 
                logger.debug("Creating entries for images in DB...")
                
                for imageData in parsedEMail[MailParser.imagesString]:
                    _insertImage(imageData, emailEntry)
                    
                logger.debug("Successfully added images to DB.")
            else:
                logger.debug("No images found in mail, not writing to DB")
                
                
                
            if fromCorrespondent:
                
                _insertEMailCorrespondent(fromCorrespondentEntry, emailEntry, constants.MENTIONS.FROM)
                
                logger.debug("Successfully added entries for FROM correspondent to DB.")
            else:
                logger.error("No FROM Correspondent found in mail, not writing to DB!")



            if parsedEMail[MailParser.toHeader]:
                logger.debug("Creating entry for TO correspondents in DB...")
                
                for toCorrespondentData in parsedEMail[MailParser.toHeader]:
                    toCorrespondentEntry = _insertCorrespondent(toCorrespondentData)
                    _insertEMailCorrespondent(emailEntry, toCorrespondentEntry, constants.MENTIONS.TO)
                    
                logger.debug("Successfully added entries for TO correspondents to DB.")
            else:
                logger.warning("No TO Correspondent found in mail, not writing to DB!")



            if parsedEMail[MailParser.ccHeader]:
                logger.debug("Creating entries for CC correspondents in DB...")
                
                for ccCorrespondentData in parsedEMail[MailParser.ccHeader]:
                    ccCorrespondentEntry = _insertCorrespondent(ccCorrespondentData)
                    _insertEMailCorrespondent(emailEntry, ccCorrespondentEntry, constants.MENTIONS.CC)
                    
                logger.debug("Successfully added entries for CC correspondents to DB.")
            else:
                logger.debug("No CC Correspondent found in mail, not writing to DB")



            if parsedEMail[MailParser.bccHeader]:
                logger.debug("Creating entries for CC correspondents in DB...")
                
                for bccCorrespondentData in parsedEMail[MailParser.bccHeader]:
                    bccCorrespondentEntry = _insertCorrespondent(bccCorrespondentData)
                    _insertEMailCorrespondent(emailEntry, bccCorrespondentEntry, constants.MENTIONS.BCC)
                    
                logger.debug("Successfully added entries for BCC correspondents to DB.")
            else:
                logger.debug("No BCC Correspondent found in mail, not writing to DB")


    except django.db.IntegrityError as e:
        logger.error("Error while writing to database, rollback to last state", exc_info=True)


