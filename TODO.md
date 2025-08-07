# ToDo

## Feature ideas

- custom fetching filters with NOT, OR and custom criteria
- combined filter for correspondent with mention
- streamable logs for daemons
- extensive database statistics
- option to prohibit daemon for spambox
- toggleable [tooltips](https://getbootstrap.com/docs/5.3/components/tooltips/)
- reprocess mail action
- mechanism to remove all correspondents without emails
- more daemon logging configs via model
- streaming daemon logs
- download for main logfiles
- fetching in bunches to handle large amounts of emails, fetch as generator
- autotest account before form submission, fetch mailboxes on submission
- [spinner](https://getbootstrap.com/docs/5.3/components/spinners/) and [progressbar](https://getbootstrap.com/docs/5.3/components/progress/) for actions
- notes field for models
- more tags
- autotagging
- saving old correspondent mailername info (via fk maybe)
- async parsing, sync saving
- auto transfer of pdfs to paperless
- fetch once by criterion instead of hardcoded ALL
- setting for thumbnail datasize threshold

## To refactor

- safeimap and pop classes
- rework test:
  - disable all signals in tests
  - tests more implementation agnostic
  - use more of the unittest api
  - replace modeltodict in form and serializer tests with payloads
- emailcorrespondent creation for better integration of mailinglist
- shorten redundant exception logging in fetchers, move parts of the messages to the exc classes
- streamline serializer and form tests

## To test

- views customactions for response with updated modeldata
- storagebackend for colliding file/dir
- test failing single message fetch (imap,pop)

## To implement

- ensure threadsafe db operations in daemons
- fetch only specific errors in fetchers
- favicon.ico for the icon
- time benchmarks in debug log
- batch download and delete in web
- dependency-upgrading tool for your project dependencies? (eg. dependabot, PyUp, Renovate, pip-tools, Snyx)
- daemonize celery worker

### Work in progress

- tests
- documentation
- type annotations

## To fix

- fetching too many emails leads to browser timeout
- running tests from test dir
- storage is incremented by healthcheck
- updating daemon logging doesnt change the daemon logger
- optics:
  - better name for daemon
  - make email on attachment a card
  - weird pagination in base-archive
  - empyt checkbox instead of xmark
  - translate validationerror
  - makemessages
- ci:
  - djlint has no files to lint
