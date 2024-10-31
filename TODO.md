implement basic exchange
maybe fetcher template superclass
maybe get rid of filesizes
custom fetching filters with NOT, OR and custom criteria
distinguish configs by env, db and user-immutables, migrate db settings to initial settings
autostart daemons on restart
custom additional healthchecks
parsing walks multiple times, could be more efficient
reconsider decoding of mailbytes using BytesParser
more spam flags
exceptions while fetching parsing and inserting for appropriate api response
more finegrain try catch in fetchers, marking as unhealthy for wrong data
marking of daemon as unhealthy, improved crashhandling
user divided storage to make file_paths unique again
some fallback for failed emailaddress parsing is required
combined filter for correspondent with mention 
documentation

# work in progress

# to test
mailbox with full decode method
parseMailbox splitting (why?)
does decodeHeader do anything. if yes it should be used more

# to fix
'Decoding this mime part returned error' for paypal in prerender
google notifcations not formatted in prerender

# at next db reset
start to use configurationmodel


# remember
new migration must include setting of defaults
logpath is misconfigured to work on windows
csrf is disabled for debug
