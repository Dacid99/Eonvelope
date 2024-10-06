implement basic exchange
attachmentdatasize kinda small
different choices for fetching depending on protocol
custom fetching filters
storageModel and fix for getStoragePath
distinguish configs by env, db and user-immutables, migrate db settings to initial settings
autostart daemons on restart
custom additional healthchecks
return serialized db data after scan and fetch_all
dbstats can be apiview
parsing walks multiple times, could be more efficient
maybe unique together account and id 
reconsider decoding of mailbytes using BytesParser

possibly move extra emailfields from emailmodel to correspondents
received should be text field
popfetcher scan mailboxes prop

# to test
restructured code

# to fix
'Decoding this mime part returned error' for paypal mail
newline characters missing (1)
XDG runtime root warning

# at next db reset
start to use configurationmodel


# remember
new migration must include setting of defaults
logpath is misconfigured to work on windows
csrf is disabled for debug
