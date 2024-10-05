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
from .LoggerFactory import LoggerFactory
from .Models.EMailModel import EMailModel
from .Models.DaemonModel import DaemonModel
from .Models.MailboxModel import MailboxModel
from .Models.AttachmentModel import AttachmentModel
from .Models.ImageModel import ImageModel
from .Models.CorrespondentModel import CorrespondentModel
from .Models.EMailCorrespondentsModel import EMailCorrespondentsModel
from .MailParser import MailParser
from . import constants

class EMailDBFeeder:
    subdirNumber = 0
    dirNumber = 0

    @staticmethod
    def insertMailbox(mailbox, account):
        logger = LoggerFactory.getChildLogger(EMailDBFeeder.__name__)

        try:
            with django.db.transaction.atomic():
                
                mailboxEntry, created = MailboxModel.objects.get_or_create(
                    name = mailbox,
                    account = account
                )
                if created:
                    logger.debug(f"Entry for {str(mailboxEntry)} created")
                    logger.debug("Attaching daemon ...")
                    newDaemon = DaemonModel.objects.create(mailbox = mailboxEntry)
                    logger.debug("Success")
                else:
                    logger.debug(f"Entry for {str(mailboxEntry)} already exists")

        except django.db.IntegrityError as e:
            logger.error("Error while writing to database, rollback to last state", exc_info=True)



    @staticmethod
    def insertEMail(parsedEMail, account):
        logger = LoggerFactory.getChildLogger(EMailDBFeeder.__name__)

        try:
            with django.db.transaction.atomic():
                
                fromCorrespondent = parsedEMail[MailParser.fromHeader]
                if fromCorrespondent:
                    fromCorrespondentEntry, created  = CorrespondentModel.objects.get_or_create(
                        email_address = fromCorrespondent[1], 
                        defaults = {'email_name': fromCorrespondent[0]}
                    )
                    if created:
                        logger.debug(f"Entry for {str(fromCorrespondentEntry)} created")
                    else:
                        logger.debug(f"Entry for {str(fromCorrespondentEntry)} already exists")
                        
                else:
                    logger.warning("No FROM Correspondent found in mail, not writing to DB!")
                    
                
                if parsedEMail[MailParser.listIDHeader]:
                    mailinglistData = parsedEMail[MailParser.listIDHeader]
                    
                    logger.debug("Creating entry for mailinglist in db...")
                    mailinglist, created = EMailModel.objects.get_or_create(
                            list_id = mailinglistData[MailParser.listIDHeader],
                            defaults= {
                                'list_owner': mailinglistData[MailParser.listOwnerHeader],
                                'list_subscribe': mailinglistData[MailParser.listSubscribeHeader],
                                'list_unsubscribe': mailinglistData[MailParser.listUnsubscribeHeader],
                                'list_post': mailinglistData[MailParser.listPostHeader],
                                'list_help': mailinglistData[MailParser.listHelpHeader],
                                'list_owner': mailinglistData[MailParser.listArchiveHeader],
                                'correspondent': fromCorrespondent
                            }
                        )
                    if created:
                        logger.debug("Created mailinglist entry")
                    else:
                        logger.debug("Mailinglist entry already exists")
                        
                
                if parsedEMail[MailParser.inReplyToHeader]:
                    try:
                        logger.debug("Querying inReplyTo mail ...")
                        inReplyToMail = EMailModel.objects.get(message_id = parsedEMail[MailParser.inReplyToHeader])
                        logger.debug("Successfully retrieved inReplyTo mail.")
                    except EMailModel.DoesNotExist:
                        logger.warning(f"Could not find inReplyTo mail {parsedEMail[MailParser.inReplyToHeader]}!")
                        inReplyToMail = None
                        
                
                logger.debug("Creating entry for email in db...")
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
                        'mailinglist': mailinglist,
                        'comments': parsedEMail[MailParser.commentsHeader],
                        'keywords': parsedEMail[MailParser.keywordsHeader],
                        'importance': parsedEMail[MailParser.importanceHeader],
                        'priority': parsedEMail[MailParser.priorityHeader],
                        'precedence': parsedEMail[MailParser.precedenceHeader],
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
                

                logger.debug("Creating entry for attachments in db...")
                
                for attachment in parsedEMail[MailParser.attachmentsString]:
                    imageEntry, created  = AttachmentModel.objects.get_or_create(
                        file_path = attachment[MailParser.attachment_filePathString],
                        email = emailEntry,
                        defaults = {
                            'file_name' : attachment[MailParser.attachment_fileNameString],
                            'datasize' : attachment[MailParser.attachment_sizeString]
                        }
                    )
                    if created:
                        logger.debug(f"Entry for {str(imageEntry)} created")
                    else:
                        logger.debug(f"Entry for {str(imageEntry)} already exists")

                if not parsedEMail[MailParser.attachmentsString]: 
                    logger.debug("No attachment files found in mail, not writing to DB")
                
                
                logger.debug("Creating entry for images in db...")
                
                for image in parsedEMail[MailParser.imagesString]:
                    imageEntry, created  = ImageModel.objects.get_or_create(
                        file_path = image[MailParser.images_filePathString],
                        email = emailEntry,
                        defaults = {
                            'file_name' : image[MailParser.images_fileNameString],
                            'datasize' : image[MailParser.images_sizeString]
                        }
                    )
                    if created:
                        logger.debug(f"Entry for {str(imageEntry)} created")
                    else:
                        logger.debug(f"Entry for {str(imageEntry)} already exists")

                if not parsedEMail[MailParser.imagesString]: 
                    logger.debug("No images found in mail, not writing to DB")
                
                
                logger.debug("Creating entry for FROM correspondents in db...")
                
                if fromCorrespondent:
                    emailCorrespondentsEntry, created = EMailCorrespondentsModel.objects.get_or_create(
                        email = emailEntry, 
                        correspondent = fromCorrespondentEntry,
                        mention = constants.MENTIONS.FROM
                    )
                    if created:
                        logger.debug(f"Entry for {str(emailCorrespondentsEntry)} created")
                    else:
                        logger.debug(f"Entry for {str(emailCorrespondentsEntry)} already exists")
                
                else:
                    logger.warning("No FROM Correspondent found in mail, not writing to DB!")


                logger.debug("Creating entry for TO correspondents in db...")
                
                for correspondent in parsedEMail[MailParser.toHeader]:
                    correspondentEntry, created  = CorrespondentModel.objects.get_or_create(
                        email_address = correspondent[1], 
                        defaults = {'email_name': correspondent[0]}
                    )
                    if created:
                        logger.debug(f"Entry for {str(correspondentEntry)} created")
                    else:
                        logger.debug(f"Entry for {str(correspondentEntry)} already exists")

                    emailCorrespondentsEntry, created = EMailCorrespondentsModel.objects.get_or_create(
                        email = emailEntry, 
                        correspondent = correspondentEntry,
                        mention = constants.MENTIONS.TO
                    )
                    if created:
                        logger.debug(f"Entry for {str(emailCorrespondentsEntry)} created")
                    else:
                        logger.debug(f"Entry for {str(emailCorrespondentsEntry)} already exists")

                if not parsedEMail[MailParser.toHeader]:
                    logger.warning("No TO Correspondent found in mail, not writing to DB!")


                logger.debug("Creating entry for CC correspondents in db...")

                for correspondent in parsedEMail[MailParser.ccHeader]:
                    correspondentEntry, created  = CorrespondentModel.objects.get_or_create(
                        email_address = correspondent[1], 
                        defaults = {'email_name': correspondent[0]}
                    )
                    if created:
                        logger.debug(f"Entry for {str(correspondentEntry)} created")
                    else:
                        logger.debug(f"Entry for {str(correspondentEntry)} already exists")

                    emailCorrespondentsEntry, created = EMailCorrespondentsModel.objects.get_or_create(
                        email = emailEntry, 
                        correspondent = correspondentEntry,
                        mention = constants.MENTIONS.CC
                    )
                    if created:
                        logger.debug(f"Entry for {str(emailCorrespondentsEntry)} created")
                    else:
                        logger.debug(f"Entry for {str(emailCorrespondentsEntry)} already exists")

                if not parsedEMail[MailParser.ccHeader]:
                    logger.debug("No CC Correspondent found in mail, not writing to DB")


                logger.debug("Creating entry for BCC correspondents in db...")

                for correspondent in parsedEMail[MailParser.bccHeader]:
                    correspondentEntry, created  = CorrespondentModel.objects.get_or_create(
                        email_address = correspondent[1], 
                        defaults = {'email_name': correspondent[0]}
                    )
                    if created:
                        logger.debug(f"Entry for {str(correspondentEntry)} created")
                    else:
                        logger.debug(f"Entry for {str(correspondentEntry)} already exists")

                    emailCorrespondentsEntry, created = EMailCorrespondentsModel.objects.get_or_create(
                        email = emailEntry, 
                        correspondent = correspondentEntry,
                        mention = constants.MENTIONS.BCC
                    )
                    if created:
                        logger.debug(f"Entry for {str(emailCorrespondentsEntry)} created")
                    else:
                        logger.debug(f"Entry for {str(emailCorrespondentsEntry)} already exists")

                if not parsedEMail[MailParser.ccHeader]:
                    logger.debug("No BCC Correspondent found in mail, not writing to DB")


        except django.db.IntegrityError as e:
            logger.error("Error while writing to database, rollback to last state", exc_info=True)


