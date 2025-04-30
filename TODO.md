# ToDo

## Feature ideas

- custom additional healthchecks
- implement basic exchange
- custom fetching filters with NOT, OR and custom criteria
- combined filter for correspondent with mention
- streamable logs for daemons
- references header
- extensive database statistics
- download mailboxes and accounts
- option to prohibit daemon for spambox
- tooltips
- archiveviews
- show pdf attachments in pdfjs
- combo queries via connectors
- reprocess mail action
- mechanism to remove all correspondents and mailinglists without emails
- more daemon logging configs via model
- streaming daemon logs
- download for main logfiles

## To refactor

- headerdict accumulation can be easier, message supports dict() or at least .items()
- check for existance is better with filter().exists()
- improve db performance with SubQuery, select_related, etc
- explore emailmessage methods
- content_type main and sub as fields and rename settings
- consistent naming_style
- move all signals into models
- base detail/edit template
- rework test:
  - consistent naming
  - disable all signals in tests
  - remove duplicate model fixtures in test/core

## To test

## To implement

- autostart daemons on restart
- user divided storage to make file_paths unique again
- replace daemons with celery, ensure threadsafe db operations in daemons
- choices for api filters
- important headers in html repr
- is_healthy null on creation
- only show allowed fetching criteria
- indicator for required form fields
- default ordering -id
- favicon.ico for the icon
- default ssl cert and safest settings
- memory save upload (chunks instead of read)
- shortcut urls (api/auth -> api/auth/login, etc)
- toggle registration switch in constance
- more settings via env (django-environ maybe)
- tests for use of cleanFilename

### Work in progress

- tests
- documentation
- type annotations

## To test hands-on

- complete app
- mailinglist

## To fix

- separation of multi correspondentheader not working!
- cascase doesnt trigger delete!
- browser is occasionally in quirks mode

# Remember

- logpath is misconfigured for makemigrations
