# ToDo

## Feature ideas

- custom additional healthchecks
- custom fetching filters with NOT, OR and custom criteria
- combined filter for correspondent with mention
- streamable logs for daemons
- extensive database statistics
- option to prohibit daemon for spambox
- toggleable [tooltips](https://getbootstrap.com/docs/5.3/components/tooltips/)
- show pdf attachments in pdfjs
- combo queries via connectors
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

## To refactor

- safeimap and pop classes
- rework test:
  - disable all signals in tests
  - tests more implementation agnostic
  - use more of the unittest api
  - replace modeltodict in form and serializer tests with payloads
- emailcorrespondent creation for better integration of mailinglist
- shorten redundant exception logging in fetchers, move parts of the messages to the exc classes

## To test

- views customactions for response with updated modeldata
- storagebackend for colliding file/dir
- test celery daemons

## To implement

- ensure threadsafe db operations in daemons
- fetch only specific errors in fetchers
- favicon.ico for the icon
- time benchmarks in debug log
- batch download and delete in web
- dependency-upgrading tool for your project dependencies? (eg. dependabot, PyUp, Renovate, pip-tools, Snyx)
- vulnerability scanning tool for your dependencies? (eg. Safety, pip-audit, Bandit, Snyx, Trivy, GitLab Dependency Scanning, PyUp, OWASP, Jake, Mend)
- daemonize celery worker
- api creation of daemons
- helptexts for orientation instead of empty lists

### For production

- rtd
- weblate

### Work in progress

- tests
- documentation
- type annotations

## To fix

- daemon logger setup doesnt persist
- running tests from test dir
- storage is incremented by healthcheck
- optics:
  - checkboxes for boolean data instead of True and False
  - better name for daemon
  - icons on mailbox detail misplaced
  - more space around welcome
  - iframes misscaled
  - remove links from thumbnail
  - contrast header key vs val
- ci:
  - djlint has no files to lint
