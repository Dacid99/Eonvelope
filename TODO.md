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

- explore emailmessage methods
- consistent naming_style
- move all signals into models
- rework test:
  - consistent naming
  - disable all signals in tests
  - remove duplicate model fixtures in test/core

## To test

- StorageModel for more cases of conflicting storage
- views customactions for response with updated modeldata
- use of cleanFilename

## To implement

- autostart daemons on restart
- user divided storage to make file_paths unique again
- replace daemons with celery, ensure threadsafe db operations in daemons
- important headers in html repr
- only show allowed fetching criteria
- favicon.ico for the icon
- default ssl cert and safest settings
- variable page size pagination
- more attachment thumbnails
- docs:
  - integratons page, searxng section in docs
- fallback for list-id if other list entries are present
- identification of mailinglists via from

### Work in progress

- tests
- documentation
- type annotations

## To test hands-on

- complete app
- mailinglist

## To fix

- cascase doesnt trigger delete!
- optics:
  - stats table out of bounds for slim viewport
