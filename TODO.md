implement basic exchange
maybe get rid of filesizes
custom fetching filters with NOT, OR and custom criteria
distinguish configs by env, db and user-immutables, migrate db settings to initial settings
autostart daemons on restart
custom additional healthchecks
parsing walks multiple times, could be more efficient
maybe unique together account and id 
reconsider decoding of mailbytes using BytesParser
more spam flags
reading from imap with uid
exceptions while fetching parsing and inserting for appropriate api response

# to test
serialized db data after scan and fetch_all

# to fix
'Decoding this mime part returned error' for paypal

# at next db reset
start to use configurationmodel


# remember
new migration must include setting of defaults
logpath is misconfigured to work on windows
csrf is disabled for debug
