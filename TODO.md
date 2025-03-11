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
- validating choices in serializers and models
- references header
- database statistics
- replace daemons with celery
- rework test:
  - consistent naming
  - unify model fixtures
  - consistent mock_open
  - complete coverage
  - extract often used fixtures
  - replace bad return_value constructions with actual mock
- emailcorrespondentsmodelserializers are inconsistent

### Work in progress

- tests
- documentation
- type annotations

## To test

- complete app

## To fix

# Remember

- logpath is misconfigured for makemigrations
