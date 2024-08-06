from POP3_SSL_Fetcher import POP3_SSL_Fetcher

import logging

#logging.basicConfig(level=logging.DEBUG)


mail = POP3_SSL_Fetcher(username="archiv@aderbauer.org", password="nxF154j9879ZZsW", host="pop.ionos.de", port=995)

parsedMails = mail.fetchAll() 
print(len(parsedMails))
for parsedMail in parsedMails:
    print(parsedMail.bodyText)