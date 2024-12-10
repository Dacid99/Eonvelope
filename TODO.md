# ToDo

## To implement
- implement basic exchange
- maybe fetcher template superclass
- maybe get rid of filesizes
- custom fetching filters with NOT, OR and custom criteria
- distinguish configs by env, db and user-immutables, migrate db settings to initial settings
- autostart daemons on restart
- custom additional healthchecks
- parsing walks multiple times, could be more efficient
- more spam flags
- exceptions while fetching parsing and inserting for appropriate api response
- handling if filename is none in parsing
- user divided storage to make file_paths unique again
- some fallback for failed emailaddress parsing is required
- combined filter for correspondent with mention
- general save function in filemanagement for DRY
- refine storage management error correction
- streamable logs for daemons
- api versioning
- assign elements to parsedMailDict in individual parser functions, leave all Null fields None, but always set all fields
- check filepath before saving files

### Work in progress
- tests
- documentation
- type annotations

## To test
- restructured project files
- filters set dynamically
- daemonsviewset and manual adding
- logfile for daemons
- health flagging in fetchers
- does decodeHeader do anything? If yes it should be used more
- fileresponse with

## To fix
- 'Decoding this mime part returned error' for paypal in prerender
- google notifcations not formatted in prerender

# Remember
- new migration must include setting of defaults
- logpath is misconfigured for makemigrations
- csrf is disabled for debug

## At next db reset
- start to use configurationmodel
