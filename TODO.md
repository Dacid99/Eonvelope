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
- reconsider decoding of mailbytes using BytesParser
- more spam flags
- exceptions while fetching parsing and inserting for appropriate api response
- test for mailbox in fetchers
- marking of daemon as unhealthy, improved crashhandling
- user divided storage to make file_paths unique again
- some fallback for failed emailaddress parsing is required
- combined filter for correspondent with mention 
- general save decorator in filemanagement
- refine storage management logging and error correction
- health flag for daemons

### Work in progress
- documentation 
- type annotations
 
## To test
- daemontest
- logfile for daemons
- mailboxparsing moved to processing
- mailbox with full decode method
- parseMailbox splitting (why?)
- does decodeHeader do anything? If yes it should be used more
- datedefault correctly formatted?

## To fix
- 'Decoding this mime part returned error' for paypal in prerender
- google notifcations not formatted in prerender
 
# Remember
- new migration must include setting of defaults
- logpath is misconfigured to work on windows
- csrf is disabled for debug

## At next db reset
- start to use configurationmodel