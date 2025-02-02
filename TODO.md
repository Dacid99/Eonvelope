# ToDo

## To implement
- implement basic exchange
- maybe fetcher template superclass
- maybe get rid of filesizes
- custom fetching filters with NOT, OR and custom criteria
- autostart daemons on restart
- custom additional healthchecks
- parsing walks multiple times, could be more efficient
- exceptions while fetching parsing and inserting for appropriate api response
- handling if filename is none in parsing
- user divided storage to make file_paths unique again
- some fallback for failed emailaddress parsing is required
- combined filter for correspondent with mention
- refine storage management error correction
- streamable logs for daemons
- check database before saving attachments and images
- registration toggling
- get rid of parsedmaildict, use models directly
- disable all signals in tests
- threadsafe db operations in daemons
- filtertest for choices
- move all signals into models
- user validation for serializers to avoid leakage

### Work in progress
- tests
- documentation
- type annotations

## To test
- health flagging in fetchers
- does decodeHeader do anything? If yes it should be used more

## To fix
- 'Decoding this mime part returned error' for paypal in prerender
- google notifcations not formatted in prerender

# Remember
- new migration must include setting of defaults
- logpath is misconfigured for makemigrations
- csrf is disabled for debug
- mailboxviewset.test and accountviewset.test are not fully tested
