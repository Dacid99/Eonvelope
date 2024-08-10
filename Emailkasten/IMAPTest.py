from IMAP_SSL_Fetcher import IMAP_SSL_Fetcher


mail = IMAP_SSL_Fetcher(username="archiv@aderbauer.org", password="nxF154j9879ZZsW", host="imap.ionos.de", port=993)

mail.fetchMailboxes()
parsedMails = mail.fetchBySearch(mailbox='"Gesendete Objekte"', searchCriterion="ALL")
for mail in parsedMails:
    print(mail.bodyText)
