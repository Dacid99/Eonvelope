# ToDo

## Feature ideas

- custom additional healthchecks
- implement basic exchange
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
- add task stats to serializer/detailview data
- autotest account before form submission, fetch mailboxes on submission
- [spinner](https://getbootstrap.com/docs/5.3/components/spinners/) and [progressbar](https://getbootstrap.com/docs/5.3/components/progress/) for actions
- notes field for models
- more tags
- autotagging
- saving old correspondent info (via fk maybe)
- async parsing, sync saving

## To refactor

- safeimap and pop classes
- move all signals into models
- navbar base template
- rework test:
  - disable all signals in tests
  - tests more implementation agnostic
  - use more of the unittest api
  - replace modeltodict in form and serializer tests with payloads
- dockerfile dependencies
- emailcorrespondent creation for better integration of mailinglist

## To test

- views customactions for response with updated modeldata
- storagebackend for colliding file/dir
- test celery daemons

## To implement

- ensure threadsafe db operations in daemons
- important headers in html repr
- favicon.ico for the icon
- time benchmarks in debug log
- batch download and delete in web
- dependency-upgrading tool for your project dependencies? (eg. dependabot, PyUp, Renovate, pip-tools, Snyx)
- vulnerability scanning tool for your dependencies? (eg. Safety, pip-audit, Bandit, Snyx, Trivy, GitLab Dependency Scanning, PyUp, OWASP, Jake, Mend)
- daemonize celery worker
- default interval setting
- interval exposure via api
- logfile for gunicorn

### For production

- rtd
- weblate
- stable docker run for makemigrations and makemessages
- test pipelines

### Work in progress

- tests
- documentation
- type annotations

## To test hands-on

- complete app
- uploads
- batch-downloads
- attachment-thumbnails
- celery daemons

## To fix

- running tests from test dir
- storage is incremented by healthcheck
- correspondent is not user specific!
- mysql may need some more care for use with timezone <https://docs.djangoproject.com/en/5.2/ref/databases/#time-zone-definitions>
- cascase doesn't trigger delete!
- optics:
  - error templates are missing margins
  - stats table out of bounds for slim viewport
