from Emailkasten.Fetchers.IMAP_SSL_Fetcher import IMAP_SSL_Fetcher
from Emailkasten.MailParsing import parseMail, ParsedMailKeys


with IMAP_SSL_Fetcher(username="archiv@aderbauer.org", password="nxF154j9879ZZsW", host="imap.ionos.de", port=993) as mail:

    mailsDataList = mail.fetchBySearch(mailbox='"Gesendete Objekte"', searchCriterion=MailProcessor.ALL)
    print(mailsDataList)
    
    for mailData in mailsDataList:
        parsedMail = parseMail(mailData)
        print(parsedMail[ParsedMailKeys.FULL_MESSAGE])
