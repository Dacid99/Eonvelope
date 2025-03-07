# ToDo

## To implement

- implement basic exchange
- custom fetching filters with NOT, OR and custom criteria
- autostart daemons on restart
- custom additional healthchecks
- user divided storage to make file_paths unique again
- combined filter for correspondent with mention
- refine storage management error correction
- streamable logs for daemons
- disable all signals in tests
- threadsafe db operations in daemons
- filtertest for choices
- move all signals into models
- user validation for serializers to avoid leakage
- enforce choices via constraint
- references header
- attachment/inline content name as first fallback for filename
- database statistics
- replace daemons with celery
- migrate to python 3.12
- rework test:
  - consistent naming
  - more autouse
  - more autospec
  - unify model fixtures
  - sort args
  - AssertionErrors for injected side_effects
  - no pytest.raises(Exception)
-remove str() where unnecessary

### Work in progress

- tests
- documentation
- type annotations

## To test

- complete app

## To fix

- mailbox names parsing doesnt match IMAP format

# Remember

- logpath is misconfigured for makemigrations
