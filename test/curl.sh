#!/bin/bash


# User registration
#curl -X POST http://192.168.178.138:1122/users/ -H "Content-Type: application/json" -d '{"username": "usr", "password": "pwd", "is_staff": true}'

# Login
#curl -i -X POST -H "Content-Type: application/json" -c cookie.txt -d '{"username": "usr", "password": "pwd", "remember": true}' http://192.168.178.138:1122/login/
#curl -b cookie.txt -H "X-CSRFToken: Dn99AeAY4wm1fje4DmSvqS6SLUla6QivL5nbisMoP6d6EaomconjLODUbACdZBE4" -X POST http://192.168.178.138:1122/logout/

# Make user staff
#curl -u usr:pwd -X PATCH -H "Content-Type: application/json" -d '{"is_staff":true}' http://192.168.178.138:1122/users/1/

# New account
#curl -u usr:pwd -X POST http://192.168.178.138:1122/accounts/ -H "Content-Type: application/json" -d '{"mail_address": "archiv@aderbauer.org", "password": "nxF154j9879ZZsW", "mail_host": "imap.ionos.de", "mail_host_port": "993", "protocol": "IMAP_SSL"}'
#curl -b cookie.txt -X POST http://192.168.178.138:1122/accounts/ -H "Content-Type: application/json" -d '{"mail_address": "archiv@aderbauer.org", "password": "nxF154j9879ZZsW", "mail_host": "imap.ionos.de", "mail_host_port": "993", "protocol": "IMAP_SSL"}'

# Test account
#curl -u usr:pwd -X POST http://192.168.178.138:1122/accounts/1/test/

# Scan mailboxes in account
#curl -u usr:pwd -X POST http://192.168.178.138:1122/accounts/1/scan_mailboxes/

# Get all mailbox data
#curl -u usr:pwd -X GET http://192.168.178.138:1122/mailboxes/
#curl -b cookie.txt -X GET http://192.168.178.138:1122/mailboxes/

# Get filtered mailbox data
#curl -u usr:pwd -X GET http://192.168.178.138:1122/mailboxes/?name__icontains=inbox

# Fetch mails in mailbox
#curl -u usr:pwd -X POST http://192.168.178.138:1122/mailboxes/12/fetch_all/

# Get data from db
#curl -u usr:pwd -X GET 'http://192.168.178.138:1122/emails/'
#curl -u usr:pwd -X GET 'http://192.168.178.138:1122/correspondents/'
#curl -u usr:pwd -X GET 'http://192.168.178.138:1122/correspondents/1/'
#curl -u usr:pwd -X GET 'http://192.168.178.138:1122/attachments/'
#curl -u usr:pwd -X GET 'http://192.168.178.138:1122/accounts/'
#curl -u usr:pwd -X GET 'http://192.168.178.138:1122/emails/?plain_bodytext__icontains=best&page_size=10&email_subject__icontains=daemon'
#curl -u usr:pwd -X GET 'http://192.168.178.138:1122/mailboxes/?protocol=IMAP_SSL&name__icontains=Archiv'

# Downloads
#curl -u usr:pwd -X GET http://192.168.178.138:1122/images/1/download/ > image.jpg
#curl -u usr:pwd -X GET http://192.168.178.138:1122/attachments/1/download/ > attachment.json
curl -u usr:pwd -X GET http://192.168.178.138:1122/mailboxes/12/daemon/log/download > daemonlog.log

# Test mailbox
#curl -u usr:pwd -X POST http://192.168.178.138:1122/mailboxes/12/test/

# Get mailbox fetching options
#curl -u usr:pwd -X GET http://192.168.178.138:1122/mailboxes/12/fetching_options/

# Change mailbox data
#curl -u usr:pwd -X PATCH http://192.168.178.138:1122/mailboxes/12/ -H "Content-Type: application/json" -d '{"daemon" : {"cycle_interval": "10"}}'
#curl -u usr:pwd -X PATCH http://192.168.178.138:1122/mailboxes/12/ -H "Content-Type: application/json" -d '{"fetching_criterion": "RECENT"}'

# Test daemon
#curl -u usr:pwd -X POST http://192.168.178.138:1122/mailboxes/12/daemon/test/
# Start daemon
#curl -u usr:pwd -X POST 'http://192.168.178.138:1122/mailboxes/12/daemon/start/'
# Stop daemon
#curl -u usr:pwd -X POST http://192.168.178.138:1122/mailboxes/12/daemon/stop/


# Get database stats
#curl -u usr:pwd -X GET 'http://192.168.178.138:1122/stats/'
