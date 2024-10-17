implement basic exchange
maybe get rid of filesizes
custom fetching filters with NOT, OR and custom criteria
distinguish configs by env, db and user-immutables, migrate db settings to initial settings
autostart daemons on restart
custom additional healthchecks
parsing walks multiple times, could be more efficient
reconsider decoding of mailbytes using BytesParser
more spam flags
exceptions while fetching parsing and inserting for appropriate api response
user divided storage to make file_paths unique again

# work in progress

# to test
unique together account and id, adapted insertion and querying
serialized db data after scan and fetch_all
imap with uid

# to fix
'Decoding this mime part returned error' for paypal

# at next db reset
start to use configurationmodel


# remember
new migration must include setting of defaults
logpath is misconfigured to work on windows
csrf is disabled for debug
