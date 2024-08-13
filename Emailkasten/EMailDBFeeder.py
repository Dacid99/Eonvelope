import logging
import traceback
import django.db
from .LoggerFactory import LoggerFactory
from .Models.EMailModel import EMailModel
from .Models.AttachmentModel import AttachmentModel
from .Models.CorrespondentModel import CorrespondentModel
from .Models.EMailCorrespondentsModel import EMailCorrespondentsModel


class EMailDBFeeder:

    MENTION_FROM = "FROM"
    MENTION_TO = "TO"
    MENTION_CC = "CC"
    MENTION_BCC = "BCC"

    @staticmethod
    def insert(parsedEMail):
        logger = LoggerFactory.getChildLogger(EMailDBFeeder.__name__)

        try:
            with django.db.transaction.atomic():
                emailEntry, created = EMailModel.objects.get_or_create(
                    message_id = parsedEMail.messageID,
                    defaults = {
                        'date_received' : parsedEMail.dateReceived,
                        'email_subject' : parsedEMail.subject,
                        'bodytext' : parsedEMail.bodyText,
                        'datasize' :  parsedEMail.dataSize,
                        'eml_filepath' : parsedEMail.emlFilePath
                    }
                )
                if created:
                    logger.debug("EmailEntry created")
                else:
                    logger.debug("EmailEntry already exists")

                for attachmentFile in parsedEMail.attachmentsFiles:
                    print(type(emailEntry))
                    print(attachmentFile)
                    attachmentEntry, created  = AttachmentModel.objects.get_or_create(
                        file_path = attachmentFile[1],
			email = emailEntry,
                        defaults = {
      			   'filename' : attachmentFile[0],
                           'datasize' : attachmentFile[2]
                        }
                    )
                    if created:
                        logger.debug("AttachmentEntry created")
                    else:
                        logger.debug("AttachmentEntry already exists")

                for correspondent in parsedEMail.emailFrom:
                    correspondentEntry, created  = CorrespondentModel.objects.get_or_create(
                        email_address = correspondent[1], 
                        defaults = {'email_name': correspondent[0]}
                    )
                    if created:
                        logger.debug("CorrespondentEntry created")
                    else:
                        logger.debug("CorrespondentEntry already exists")
                   

                    EMailCorrespondentsEntry, created = EMailCorrespondentsModel.objects.get_or_create(
                        email = emailEntry, 
                        correspondent = correspondentEntry,
                        mention = EMailDBFeeder.MENTION_FROM
                    )
                    if created:
                        logger.debug("EmailCorrespondentEntry with FROM created")
                    else:
                        logger.debug("EmailCorrespondentEntry with FROM already exists")

                for correspondent in parsedEMail.emailTo:
                    correspondentEntry, created  = CorrespondentModel.objects.get_or_create(
                        email_address = correspondent[1], 
                        defaults = {'email_name': correspondent[0]}
                    )
                    if created:
                        logger.debug("CorrespondentEntry created")
                    else:
                        logger.debug("CorrespondentEntry already exists")

                    EMailCorrespondentsEntry, created = EMailCorrespondentsModel.objects.get_or_create(
                        email = emailEntry, 
                        correspondent = correspondentEntry,
                        mention = EMailDBFeeder.MENTION_TO
                    )
                    if created:
                        logger.debug("EmailCorrespondentEntry with TO created")
                    else:
                        logger.debug("EmailCorrespondentEntry with TO already exists")
                
                for correspondent in parsedEMail.emailCc:
                    correspondentEntry, created  = CorrespondentModel.objects.get_or_create(
                        email_address = correspondent[1], 
                        defaults = {'email_name': correspondent[0]}
                    )
                    if created:
                        logger.debug("CorrespondentEntry created")
                    else:
                        logger.debug("CorrespondentEntry already exists")

                    EMailCorrespondentsEntry, created = EMailCorrespondentsModel.objects.get_or_create(
                        email = emailEntry, 
                        correspondent = correspondentEntry,
                        mention = EMailDBFeeder.MENTION_CC
                    )
                    if created:
                        logger.debug("EmailCorrespondentEntry with CC created")
                    else:
                        logger.debug("EmailCorrespondentEntry with CC already exists")

                for correspondent in parsedEMail.emailBcc:
                    correspondentEntry, created  = CorrespondentModel.objects.get_or_create(
                        email_address = correspondent[1], 
                        defaults = {'email_name': correspondent[0]}
                    )
                    if created:
                        logger.debug("CorrespondentEntry created")
                    else:
                        logger.debug("CorrespondentEntry already exists")

                    EMailCorrespondentsEntry, created = EMailCorrespondentsModel.objects.get_or_create(
                        email = emailEntry, 
                        correspondent = correspondentEntry,
                        mention = EMailDBFeeder.MENTION_BCC
                    )
                    if created:
                        logger.debug("EmailCorrespondentEntry with BCC created")
                    else:
                        logger.debug("EmailCorrespondentEntry with BCC already exists")


        except django.db.IntegrityError as e:
            logger.error("Error while writing to database, rollback to last state", exc_info=True)


