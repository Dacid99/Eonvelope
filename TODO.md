implement basic exchange
maybe get rid of filesizes
different choices for fetching depending on protocol
custom fetching filters
distinguish configs by env, db and user-immutables, migrate db settings to initial settings
autostart daemons on restart
custom additional healthchecks
return serialized db data after scan and fetch_all
parsing walks multiple times, could be more efficient
maybe unique together account and id 
reconsider decoding of mailbytes using BytesParser
option to throw spam out by default

# to test

# to fix
'Decoding this mime part returned error' for paypal

# at next db reset
start to use configurationmodel


# remember
new migration must include setting of defaults
logpath is misconfigured to work on windows
csrf is disabled for debug
