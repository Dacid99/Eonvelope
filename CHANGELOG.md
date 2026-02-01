# Changelog

## Version 0.5.3

- Features:
  - download for account
  - batch-download for mailboxes

## Version 0.5.2

- Features:
  - setting to allow insecure connections for IMAP, POP and JMAP
  - performance improvements for email search

- Fixes:
  - filtering and searching by header-name now works
  - removed unsupported filter types
  - routine detail page was not linked on routine list page

## Version 0.5.1

- Hotfix: there was a bad import path

## Version 0.5.0

- Features:
  - simplified setup of routines to archive entire mailtraffic of an account
  - mailboxes are automatically retrieved for new accounts
  - email searchbar on dashboard

- Fixes:
  - data import and export in admin panel was broken
  - in some edge cases exchange would not use the configured timeout value
  - bad configuration of an Exchange account lead to an internal server error
  - bad JMAP server addresses could result in uncaught internal error


## Version 0.4.0

- Features:
  - support for JMAP protocol
  - more fetching criteria
  - fetching criteria with custom filter value

- Fixes:
  - year values in timeline week overview were incorrectly formatted

## Version 0.3.0

- Features:
  - slim mode for use on systems with restricted resources
  - customized adminpanel
  - automatic testing of account when created or updated
  - update mailboxes now also updates their health flags

## Version 0.2.3

- Features:
  - thumbnails for attachment mimetypes calendar and vcard
  - selection for list or table now via dropdown from navbar
  - slightly extended stats on dashboard
  - small extensions of some api endpoints

- Fixes:
  - improved mobile interface
  - fixed pwa getting stuck on offline page
  - email x-spam data is now easier to filter by
  - autohiding apikey and passwords in profile settings
  - ordering of mailboxes by account first, name second to get a less confusing list

## Version 0.2.2

- Features:
  - builds for arm64

- Fixes:
  - some buttons in the ui didn't work as expected

- Updates:
  - dependencies

## Version 0.2.1

- Features:
  - rebranded to Eonvelope
  - added icons

- Fixes:
  - PWA is working now

- Updates:
  - translations
  - dependencies

## Version 0.2.0

- Features:
  - Table interface as alternative to card lists
  - Integration with Prometheus
  - Database export and import in the admin panel

- Fixes:
  - mailbox names for some servers were parsed incorrectly
  - accepting subject lines of length > 255 chars
  - limit on current emails on the dashboard
  - clarified deletion notes
  - fixed api authentication via X-Session-Token

## Version 0.1.0

- Features
  - user profiles
  - multi-factor-authentication
  - complete API authentication endpoints
  - Sharing attachments to Paperless-ngx
  - Restoring emails to the mailaccount
  - improved email-conversation lookup with dedicated page
  - more detailed error management for accounts and mailboxes

- Fixes
  - completed API schema documentation
  - streamlined API response fields

## Version 0.0.1

- First public version
