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
- emailcorrespondent creation for better integration of mailinglist
- use pre-commit

## To test

- views customactions for response with updated modeldata
- storagebackend for colliding file/dir
- test failing single message fetch (imap,pop)
- page_obj of list views for correct email content
- remove values in action test-requests

## To implement

- fetch only specific errors in fetchers
- favicon.ico for the icon
- daemonize celery worker

### Work in progress

- tests
- documentation
- type annotations

## To fix

- filteroptions for existing db entries leak other user data
- fetching too many emails leads to browser timeout
- optics:
  - forms in btn-toolbar break optics
  - better name for daemon
- ci:
  - djlint has no files to lint
