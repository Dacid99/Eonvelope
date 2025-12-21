# ToDo

## Feature ideas

- custom fetching filters with NOT, OR and custom criteria
- combined filter for correspondent with mention
- extensive database statistics
- toggleable [tooltips](https://getbootstrap.com/docs/5.3/components/tooltips/)
- mechanism to remove all correspondents without emails
- download for main logfiles
- fetching in bunches to handle large amounts of emails, fetch as generator
- autofetch mailboxes on submission
- [progressbar](https://getbootstrap.com/docs/5.3/components/progress/) for actions
- notes field for models
- more tags
- autotagging
- async parsing, sync saving
- download for account and batchdownload for mailbox
- show pwd button
- add jmap protocol

## To refactor

- safeimap and pop classes
- rework test:
  - disable all signals in tests
  - tests more implementation agnostic
  - use more of the unittest api
  - streamline serializer and form tests
- emailcorrespondent creation for better integration of mailinglist
- use pre-commit
- split up long functions that are marked as too complex by ruff

## To test

- storagebackend for colliding file/dir
- test failing single message fetch (imap,pop)
- page_obj of list views for correct email content
- add test email with references

## To implement

- migration to django6.0

### Work in progress

- tests
- documentation
- type annotations

## To fix

- form errors not shown in account edit page (https://django-bootstrap5.readthedocs.io/en/latest/templatetags.html)
- filteroptions for existing db entries leak other user data
- fetching too many emails leads to browser timeout
- ci:
  - djlint has no files to lint
