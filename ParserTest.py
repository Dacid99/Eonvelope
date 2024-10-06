import email
import email.header
import email_validator
import logging

def decodeHeader(header):
    decodedFragments = email.header.decode_header(header)
    decodedString = ""
    for fragment, charset in decodedFragments:
        if charset is None:
            decodedString += fragment.decode('utf-8', errors='replace') if isinstance(fragment, bytes) else fragment
        else:
            decodedString += fragment.decode(charset, errors='replace')

    return decodedString

def separateRFC2822MailAddressFormat(mailer):
    mailName, mailAddress = email.utils.parseaddr(mailer)
    try:
        email_validator.validate_email(mailAddress, check_deliverability=False)
    except email_validator.EmailNotValidError:
        logging.warning(f"Separation of mailname and address failed for {mailer}!")
        mailAddress = mailer 
    
    return (mailName, mailAddress)

test = None
result = separateRFC2822MailAddressFormat(decodeHeader(test))[1]

print(result)