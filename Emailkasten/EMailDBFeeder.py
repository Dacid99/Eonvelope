import django.db
from .LoggerFactory import LoggerFactory
from .Models.EMailModel import EMailModel
from .Models.MailboxModel import MailboxModel
from .Models.AttachmentModel import AttachmentModel
from .Models.CorrespondentModel import CorrespondentModel
from .Models.EMailCorrespondentsModel import EMailCorrespondentsModel
from .MailParser import MailParser

class EMailDBFeeder:

    MENTION_FROM = "FROM"
    MENTION_TO = "TO"
    MENTION_CC = "CC"
    MENTION_BCC = "BCC"

    @staticmethod
    def insertMailboxes(mailboxesList, account):
        logger = LoggerFactory.getChildLogger(EMailDBFeeder.__name__)

        try:
            with django.db.transaction.atomic():
                for mailbox in mailboxesList:
                    mailboxEntry, created = MailboxModel.objects.get_or_create(
                        name = mailbox,
                        account = account
                    )
                    if created:
                        logger.debug(f"Entry for {str(mailboxEntry)} created")
                    else:
                        logger.debug(f"Entry for {str(mailboxEntry)} already exists")

        except django.db.IntegrityError as e:
            logger.error("Error while writing to database, rollback to last state", exc_info=True)



    @staticmethod
    def insertEMail(parsedEMail, account):
        logger = LoggerFactory.getChildLogger(EMailDBFeeder.__name__)

        try:
            with django.db.transaction.atomic():
                emailEntry, created = EMailModel.objects.get_or_create(
                    message_id = parsedEMail[MailParser.messageIDString],
                    defaults = {
                        'datetime' : parsedEMail[MailParser.dateString],
                        'email_subject' : parsedEMail[MailParser.subjectString],
                        'bodytext' : parsedEMail[MailParser.bodyTextString],
                        'datasize' :  parsedEMail[MailParser.sizeString],
                        'eml_filepath' : parsedEMail[MailParser.emlFilePathString],
                        'account' : account
                    }
                )
                if created:
                    logger.debug(f"Entry for {str(emailEntry)} created")
                else:
                    logger.debug(f"Entry for {str(emailEntry)} already exists")
                

                
                for attachment in parsedEMail[MailParser.attachmentsString]:
                    attachmentEntry, created  = AttachmentModel.objects.get_or_create(
                        file_path = attachment[MailParser.attachment_filePathString],
                        email = emailEntry,
                        defaults = {
                            'file_name' : attachment[MailParser.attachment_fileNameString],
                            'datasize' : attachment[MailParser.attachment_sizeString]
                        }
                    )
                    if created:
                        logger.debug(f"Entry for {str(attachmentEntry)} created")
                    else:
                        logger.debug(f"Entry for {str(attachmentEntry)} already exists")

                if not parsedEMail[MailParser.attachmentsString]: 
                    logger.debug("No attachment files found in mail, not writing to DB")


                
                correspondent = parsedEMail[MailParser.fromString]
                if correspondent:
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
                        mention = EMailDBFeeder.MENTION_FROM
                    )
                    if created:
                        logger.debug(f"Entry for {str(emailCorrespondentsEntry)} created")
                    else:
                        logger.debug(f"Entry for {str(emailCorrespondentsEntry)} already exists")
                
                else:
                    logger.warning("No FROM Correspondent found in mail, not writing to DB!")

                
                for correspondent in parsedEMail[MailParser.toString]:
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
                        mention = EMailDBFeeder.MENTION_TO
                    )
                    if created:
                        logger.debug(f"Entry for {str(emailCorrespondentsEntry)} created")
                    else:
                        logger.debug(f"Entry for {str(emailCorrespondentsEntry)} already exists")

                if not parsedEMail[MailParser.toString]:
                    logger.warning("No TO Correspondent found in mail, not writing to DB!")


                for correspondent in parsedEMail[MailParser.ccString]:
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
                        mention = EMailDBFeeder.MENTION_CC
                    )
                    if created:
                        logger.debug(f"Entry for {str(emailCorrespondentsEntry)} created")
                    else:
                        logger.debug(f"Entry for {str(emailCorrespondentsEntry)} already exists")

                if not parsedEMail[MailParser.ccString]:
                    logger.debug("No CC Correspondent found in mail, not writing to DB")


                for correspondent in parsedEMail[MailParser.bccString]:
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
                        mention = EMailDBFeeder.MENTION_BCC
                    )
                    if created:
                        logger.debug(f"Entry for {str(emailCorrespondentsEntry)} created")
                    else:
                        logger.debug(f"Entry for {str(emailCorrespondentsEntry)} already exists")

                if not parsedEMail[MailParser.ccString]:
                    logger.debug("No BCC Correspondent found in mail, not writing to DB")


        except django.db.IntegrityError as e:
            logger.error("Error while writing to database, rollback to last state", exc_info=True)


