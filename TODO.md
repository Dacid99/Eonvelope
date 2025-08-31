# ToDo

## Feature ideas

- custom fetching filters with NOT, OR and custom criteria
- combined filter for correspondent with mention
- extensive database statistics
- toggleable [tooltips](https://getbootstrap.com/docs/5.3/components/tooltips/)
- reprocess mail action
- mechanism to remove all correspondents without emails
- download for main logfiles
- fetching in bunches to handle large amounts of emails, fetch as generator
- autotest account before form submission, fetch mailboxes on submission
- [progressbar](https://getbootstrap.com/docs/5.3/components/progress/) for actions
- notes field for models
- more tags
- autotagging
- saving old correspondent mailername info (via fk maybe)
- async parsing, sync saving
- auto transfer of pdfs to paperless
- use post-unsubscribe-method to interpret post-unsubscribe as link
- batch download and delete in web
- download for account
- mechanism to add missing connections between emails

## To refactor

- safeimap and pop classes
- rework test:
  - disable all signals in tests
  - tests more implementation agnostic
  - use more of the unittest api
  - replace modeltodict in form and serializer tests with payloads
  - streamline serializer and form tests
  - fake_error_message as global fixture
- emailcorrespondent creation for better integration of mailinglist
- use pre-commit

## To test

- views customactions for response with updated modeldata
- storagebackend for colliding file/dir
- test failing single message fetch (imap,pop)
- page_obj of list views for correct email content

## To implement

- fetch only specific errors in fetchers
- last_error for mailbox and account
- favicon.ico for the icon
- daemonize celery worker

### Work in progress

- tests
- documentation
- type annotations

## To fix

- fetching too many emails leads to browser timeout
- optics:
  - no extra cards in conversation, use lists or similar instead
  - conversation always exists, check for count>1 instead
  - better name for daemon
  - theme toggler dropdown on right (wrong) side in folded mode
  - footer breaks in bad place in folded mode
  - footer should be in emailkasten templates
- ci:
  - djlint has no files to lint
