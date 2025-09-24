# ToDo

## Feature ideas

- custom fetching filters with NOT, OR and custom criteria
- combined filter for correspondent with mention
- extensive database statistics
- toggleable [tooltips](https://getbootstrap.com/docs/5.3/components/tooltips/)
- mechanism to remove all correspondents without emails
- download for main logfiles
- fetching in bunches to handle large amounts of emails, fetch as generator
- autotest account before form submission, fetch mailboxes on submission
- [progressbar](https://getbootstrap.com/docs/5.3/components/progress/) for actions
- notes field for models
- more tags
- autotagging
- async parsing, sync saving
- use post-unsubscribe-method to interpret post-unsubscribe as link
- download for account and batchdownload for mailbox

## To refactor

- safeimap and pop classes
- rework test:
  - disable all signals in tests
  - tests more implementation agnostic
  - use more of the unittest api
  - streamline serializer and form tests
- emailcorrespondent creation for better integration of mailinglist
- use pre-commit

## To test

- views customactions for response with updated modeldata
- storagebackend for colliding file/dir
- test failing single message fetch (imap,pop)
- page_obj of list views for correct email content
- add test email with references

## To implement

- favicon.ico for the icon
- daemonize celery worker

### Work in progress

- tests
- documentation
- type annotations

## To fix

- filteroptions for existing db entries leak other user data
- fetching too many emails leads to browser timeout
- ci:
  - djlint has no files to lint
