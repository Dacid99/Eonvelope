implement basic exchange
restructure filemanager
different choices for fetching depending on protocol
custom fetching filters
storageModel and fix for getStoragePath
distinguish configs by env, db and user-immutables, migrate db settings to initial settings
autostart daemons on restart
custom additional healthchecks
return serialized db data after scan and fetch_all
parsing walks multiple times, could be more efficient
saving images and attachments is done even if theyre already in db
maybe unique together account and id 
reconsider decoding of mailbytes using BytesParser


# to test
filesizes fix
xdg path message
attachment recognition
db stats api

# to fix
'Decoding this mime part returned error' for paypal mail
newline characters missing (1)

# at next db reset
start to use configurationmodel


# remember
new migration must include setting of defaults
logpath is misconfigured to work on windows
csrf is disabled for debug
