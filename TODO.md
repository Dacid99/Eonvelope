# ToDo

## Feature ideas

- combined filter for correspondent with mention
- extensive database statistics
- toggleable [tooltips](https://getbootstrap.com/docs/5.3/components/tooltips/) or [popovers](https://developer.chrome.com/blog/popover-hint?hl=de)
- mechanism to remove all correspondents without emails
- download for main logfiles
- fetching in bunches to handle large amounts of emails, fetch as generator
- [progressbar](https://getbootstrap.com/docs/5.3/components/progress/) for actions
- notes field for models
- tagging system with [django-tagging](https://django-tagging.readthedocs.io/en) of [taggit](https://django-taggit.readthedocs.io/en/latest/)
- autotagging
- async parsing, sync saving
- download for account and batchdownload for mailbox
- show pwd button
- structured json based logging messages
- refine fetchererrors into errors for auth, connection, etc.
- add gmail client support

## To refactor

- safeimap and pop classes
- rework test:
  - tests more implementation agnostic
  - use more of the unittest api
  - streamline serializer and form tests
- emailcorrespondent creation for better integration of mailinglist
- split up long functions that are marked as too complex by ruff
- make all filepaths pathlib.Paths
- compress fetchingcriterion logic into a class

## To test

- storagebackend for colliding file/dir
- test failing single message fetch (imap, pop, jmap)
- page_obj of list views for correct email content
- add test email with references

## To implement

- migration to django6.0
- squashmigrations
- further optimize queryset lookups

### Work in progress

- tests
- documentation
- type annotations

## To fix

- filteroptions for existing db entries leak other user data
- fetching too many emails leads to browser timeout
- ci:
  - djlint has no files to lint
