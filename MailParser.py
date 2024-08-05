import email 
import email.header
import email.utils
import email.generator
import logging
import os.path

from ParsedEMail import ParsedEMail

class MailParser:
    __messageIDString = "Message-ID"
    __fromString = "From"
    __toString = "To"
    __bccString = "Bcc"
    __ccString = "Cc"
    __dateString = "Date"
    __subjectString = "Subject"
    __charsetDefault = "utf-8"
    __dateFormat = '%Y-%m-%d %H:%M:%S'
    __dateDefault = "1971-01-01 00:00:00"  #must fit dateFormat
    emlDirectoryPath = "/mnt/eml/"

    @staticmethod
    def parse(mailToParse):
        self.logger = logging.getLogger(EMailArchiverDaemon.loggerName + MailParser.__name__)

        mailMessage = email.message_from_bytes(mailToParse)
        self.logger.debug(f"Parsing email with content\n{mailMessage}\n ...")

        def decodeHeader(header):
            self.logger.debug("Decoding header ...")

            decodedFragments = email.header.decode_header(header)
            decodedString = ""
            for fragment, charset in decodedFragments:
                if charset is None:
                    decodedString += fragment.decode(MailParser.__charsetDefault, errors='replace') if isinstance(fragment, bytes) else fragment
                else:
                    decodedString += fragment.decode(charset, errors='replace')

            self.logger.debug("Success")
            return decodedString


        def decodeText(text):
            self.logger.debug("Decoding text ...")

            charset = text.get_content_charset()
            if charset is None:
                charset = MailParser.__charsetDefault
            decodedText = text.get_payload(decode=True).decode(charset, errors='replace')

            self.logger.debug("Success")
            return decodedText
        

        def separateMailNameAndAdress(mailer):
            mailName, mailAddress = email.utils.parseaddr(mailer)
            if mailAddress.find("@") == -1:
                self.logger.warn(f"Separation of mailname and address failed for {mailer}!")
                mailAddress = mailer
            
            return (mailName, mailAddress)
        

        def parseMessageID():
            messageID = mailMessage.get(MailParser.__messageIDString)
            if messageID is None:
                self.logger.warn(f"No messageID found in mail\n{mailMessage}\n\nresorting to hash!")
                return str(hash(mailMessage))  #fallback for unique identifier if no messageID found
            return messageID

        def parseFrom():
            sender = mailMessage.get(MailParser.__fromString)
            if sender is None:
                self.logger.warn(f"No FROM correspondent found in mail\n{mailMessage}!")
                return None
            return separateMailNameAndAdress(decodeHeader(sender))

        def parseTo():
            recipients = mailMessage.get_all(MailParser.__toString)
            if recipients is None:
                self.logger.warn(f"No TO correspondents found in mail\n{mailMessage}!")
                return []
            decodedAndSeparatedRecipients = [separateMailNameAndAdress(decodeHeader(recipient)) for recipient in recipients]
            return decodedAndSeparatedRecipients
        
        def parseBcc():
            recipients = mailMessage.get_all(MailParser.__bccString)
            if recipients is None:
                self.logger.debug("No BCC correspondents found in mail")
                return []
            decodedAndSeparatedRecipients = [separateMailNameAndAdress(decodeHeader(recipient)) for recipient in recipients]
            return decodedAndSeparatedRecipients
        
        def parseCc():
            recipients = mailMessage.get_all(MailParser.__ccString)
            if recipients is None:
                self.logger.debug("No CC correspondents found in mail")
                return []
            decodedAndSeparatedRecipients = [separateMailNameAndAdress(decodeHeader(recipient)) for recipient in recipients]
            return decodedAndSeparatedRecipients

        def parseDate():
            date = mailMessage.get(MailParser.__dateString)
            if date is None:
                self.logger.warn(f"No DATE found in mail\n{mailMessage}\n\nresorting to default!")
                return MailParser.__dateDefault
            decodedDate = decodeHeader(date)
            decodedConvertedDate = email.utils.parsedate_to_datetime(decodedDate).strftime(MailParser.__dateFormat)
            return decodedConvertedDate
        
        def parseSubject():
            if (subject := mailMessage.get(MailParser.__subjectString)):
                return decodeHeader(subject)
            else: 
                self.logger.warn(f"No SUBJECT found in mail\n{mailMessage}!")
                return ""
        
        def parseBody():
            mailBodyText = ""
            if mailMessage.is_multipart():
                for text in mailMessage.walk():
                    if text.get_content_type() in ['text/plain', 'text/html']:
                        mailBodyText += decodeText(text)
            else:
                mailBodyText = decodeText(mailMessage)
            if mailBodyText == "":
                self.logger.warn(f"No BODYTEXT found in mail\n{mailMessage}!")
            return mailBodyText

        def generateEML():
            self.logger.debug("Storing mail in .eml file ...")
            emlFilePath = os.path.join(MailParser.emlDirectoryPath, parseSubject() + ".eml")
            try:
                if os.path.exists(emlFilePath):
                    if os.path.getsize(emlFilePath) > 0:
                        self.logger.debug(f"Not writing to {emlFilePath}, it already exists and is not empty")
                        return emlFilePath
                    else:
                        self.logger.debug(f"Writing to empty .eml file {emlFilePath}...")
                        with open(emlFilePath, "wb") as emlFile:
                            emlGenerator = email.generator.BytesGenerator(emlFile)
                            emlGenerator.flatten(mailMessage)
                        self.logger.debug("Success")
                else:
                    self.logger.debug(f"Creating new .eml file {emlFilePath}...")
                    with open(emlFilePath, "wb") as emlFile:
                        emlGenerator = email.generator.BytesGenerator(emlFile)
                        emlGenerator.flatten(mailMessage)
                    self.logger.debug("Success")

            except OSError as e:
               self.logger.error(f"Failed to write .eml file for message\n{mailMessage}!", exc_info=True)

            return emlFilePath


        
        parsedEMail = ParsedEMail()
        parsedEMail.messageID = parseMessageID()
        parsedEMail.subject = parseSubject()
        parsedEMail.emailFrom = parseFrom()
        parsedEMail.emailTo = parseTo()
        parsedEMail.emailCc = parseCc()
        parsedEMail.emailBcc = parseBcc()
        parsedEMail.dateReceived = parseDate()
        parsedEMail.bodyText = parseBody()
        parsedEMail.emlFilePath = generateEML()

        self.logger.debug("Success")
        return parsedEMail