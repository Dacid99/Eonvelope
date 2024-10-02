implement basic exchange
emaildbfeeder and mailparser should be factories or something more maintainable than right now
attachmentdatasize kinda small
different choices for fetching depending on protocol
custom fetching filters
storageModel
distinguish configs by env, db and user-immutables, migrate db settings to initial settings
autostart daemons on restart
custom additional healthchecks
restructure logging
return serialized db data after scan and fetch_all
loginout
dbstats can be apiview

# to test

# to fix
permission inheritance is misleading

# at next db reset
start to use configurationmodel


# remember
new migration must include setting of defaults
logpath is misconfigured to work on windows
csrf is disabled for debug
