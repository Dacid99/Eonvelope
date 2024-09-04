#!/bin/bash

#use-case scenario
#curl -X POST http://192.168.178.138:1122/register/ -H "Content-Type: application/json" -d '{"username": "usr", "password": "pwd"}' 
#curl -u usr:pwd -X POST http://192.168.178.138:1122/accounts/ -H "Content-Type: application/json" -d '{"mail_address": "archiv@aderbauer.org", "password": "nxF154j9879ZZsW", "mail_host": "imap.ionos.de", "mail_host_port": "993", "protocol": "IMAP_SSL"}' 
#curl -u usr:pwd -X POST http://192.168.178.138:1122/accounts/1/test/
#curl -u usr:pwd -X POST http://192.168.178.138:1122/accounts/1/scan_mailboxes/
#curl -u usr:pwd -X GET http://192.168.178.138:1122/mailboxes/
#curl -u usr:pwd -X GET http://192.168.178.138:1122/mailboxes/?name__icontains=inbox
#curl -u usr:pwd -X POST http://192.168.178.138:1122/mailboxes/5/fetch_all/
#curl -u usr:pwd -X GET 'http://192.168.178.138:1122/emails/'
curl -u usr:pwd -X GET 'http://192.168.178.138:1122/correspondents/'
#curl -u usr:pwd -X GET 'http://192.168.178.138:1122/correspondents/1/'
#curl -u usr:pwd -X GET 'http://192.168.178.138:1122/attachments/'
#curl -u usr:pwd -X GET 'http://192.168.178.138:1122/accounts/'
#curl -u usr:pwd -X GET 'http://192.168.178.138:1122/emails/?bodytext__icontains=best&page_size=10&email_subject__icontains=daemon'
#curl -u usr:pwd -X GET 'http://192.168.178.138:1122/mailboxes/?protocol=IMAP_SSL&name__icontains=Archiv'
#curl -u usr:pwd -X POST 'http://192.168.178.138:1122/mailboxes/5/start/'
#curl -u usr:pwd -X PATCH http://192.168.178.138:1122/mailboxes/1/ -H "Content-Type: application/json" -d '{"fetching_criterion": "ALL", "daemon" : {"cycle_interval": "10"}}'
#curl -u usr:pwd -X POST http://192.168.178.138:1122/mailboxes/5/stop/
#curl -u usr:pwd -X GET 'http://192.168.178.138:1122/stats/'
