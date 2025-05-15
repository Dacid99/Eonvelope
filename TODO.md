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
- fetching in bunches to handle large amounts of emails, fetch as generator

## To refactor

- consistent naming_style
- move all signals into models
- rework test:
  - consistent naming
  - disable all signals in tests

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
- more attachment thumbnails
- fallback for list-id if other list entries are present
- identification of mailinglists via from
- time benchmarks in debug log

### Work in progress

- tests
- documentation
- type annotations

## To test hands-on

- complete app
- mailinglist

## To fix

- mysql may need some more care for use with timezone <https://docs.djangoproject.com/en/5.2/ref/databases/#time-zone-definitions>
- cascase doesnt trigger delete!
- optics:
  - stats table out of bounds for slim viewport
