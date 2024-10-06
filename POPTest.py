from Emailkasten.Fetchers.POP3_SSL_Fetcher import POP3_SSL_Fetcher
from Emailkasten.MailParsing import parseMail, ParsedMailKeys
from Emailkasten.MailProcessor import MailProcessor


with POP3_SSL_Fetcher(username="archiv@aderbauer.org", password="nxF154j9879ZZsW", host="pop.ionos.de", port=995) as mail:

    mailsDataList = mail.fetchAll() 
    print(mailsDataList)

    for mailData in mailsDataList:
        parsedMail = parseMail(mailData)
        print(parsedMail[ParsedMailKeys.FULL_MESSAGE])