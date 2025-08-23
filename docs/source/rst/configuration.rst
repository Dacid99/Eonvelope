..
   SPDX-License-Identifier: CC-BY-SA 4.0

   Copyright (C) 2024 David Aderbauer & The Emailkasten Contributors
   Licensed under the Creative Commons Attribution-ShareAlike 4.0 International License.

Configuration
=============

The configuration for Emailkasten is divided into 3 levels:

- **Server admin**: Can only be changed by the server admin hosting the Emailkasten instance
- **Admin user**: Can only be changed by an admin or staff user in the Emailkasten instance
- **Any user**: Can be changed by and for any individual user

The more people have access to the settings, the less security-relevant they are.

*All settings have reasonable and safe defaults.*

Server Admin Settings
---------------------

These settings are stored in environmental variables
that can be adapted via the ``docker-compose.yml`` file.

You can check out the docker-compose files in the repository for further reference.

Mandatory
^^^^^^^^^

+---------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Setting                   | Description                                                                                                                                                                                                             |
+===========================+=========================================================================================================================================================================================================================+
| SECRET_KEY                | A random string, the longer the better. This is the essential unit of Django's cryptography functionalities and must not be disclosed ever!                                                                             |
+---------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| DATABASE                  | The name of the database in the MariaDB. Must match the ``MARIADB_DATABASE`` value of the MariaDB config.                                                                                                               |
+---------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| DATABASE_USER             | The username for the MariaDB. Must match the ``MARIADB_USER`` value of the MariaDB config.                                                                                                                              |
+---------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| DATABASE_PASSWORD         | The user's password for the MariaDB. Must match the ``MARIADB_PASSWORD`` value of the MariaDB config.                                                                                                                   |
+---------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| DJANGO_SUPERUSER_PASSWORD | The password of the Emailkasten admin user that is created by default. Pick a secure password and keep it safe. Access to the admin allows access to the database so if an attacker gets a hold of this it's game over. |
+---------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ALLOWED_HOSTS             | The hostnames that the application is served from, as a comma separated list. Select this restrictively, it guards against man-in-the-middle type attacks. *localhost* is always included.                              |
+---------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

Optional
^^^^^^^^

+------------------------+------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Setting                | Default    | Description                                                                                                                                                                                                                                 |
+========================+============+=============================================================================================================================================================================================================================================+
| APP_LOG_LEVEL          | `INFO`     | The log level of the Emailkasten logger. It logs to Emailkasten.log in the logs docker volume and contains information about events in the Emailkasten application components.                                                              |
+------------------------+------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| DJANGO_LOG_LEVEL       | `INFO`     | The log level of the Django logger. It logs to django.log in the logs docker volume and contains information about events in the Django library components.                                                                                 |
+------------------------+------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| CELERY_LOG_LEVEL       | `INFO`     | The log level of the logger for celery. It logs to only to celery.log in the logs docker volume and contains information about events in the celery event queue.                                                                            |
+------------------------+------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| AMQP_LOG_LEVEL         | `INFO`     | The log level of the logger for amqp components. It logs only to amqp.log in the logs docker volume and contains information about events in the connection to the rabbitmq messagebroker.                                                  |
+------------------------+------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| LOGFILE_MAXSIZE        | `10485760` | The maximum size for a single log file in bytes. This should not be too large so the log files can be read with a standard editor.                                                                                                          |
+------------------------+------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| LOGFILE_BACKUP_NUMBER  | `5`        | The number of log files to keep in the backstack. This number should be higher the lower your log level.                                                                                                                                    |
+------------------------+------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| RECONNECT_DELAY        | `10`       | The time between two reconnection attempts to the database.                                                                                                                                                                                 |
+------------------------+------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| RECONNECT_RETRIES      | `10`       | The number of reconnect attempts before raising an error.                                                                                                                                                                                   |
+------------------------+------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| REGISTRATION_ENABLED   | `False`    | Set this to `True` to allow self-sign-on. Set this to `False`, if you never want users to sign on themselves, so only staff members can create new user accounts. If True, the admin level ``REGISTRATION_ENABLED`` setting becomes active. |
+------------------------+------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| GUNICORN_WORKER_NUMBER | `1`        | The number of worker processes serving the webpages. For better load balancing set this to 2-4 * NUM_CORES, as recommended by the `gunicorn docs <https://docs.gunicorn.org/en/stable/settings.html#workers>`                               |
+------------------------+------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| STRICT_PASSWORDS       | `True`     | Set this to `True` to have user passwords strictly validated for length, commonness and simplicity.                                                                                                                                         |
+------------------------+------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| DEBUG                  | `False`    | Set this to `True` to run the application in debug mode. Do not activate this unless you're trying to debug an issue and are not exposing the debug instance.                                                                               |
+------------------------+------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+


Admin User Settings
-------------------

These settings can be found and managed in the Django admin interface at */admin*.
They are sorted into categories:

+------------------------------------+-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Setting                            | Default                 | Description                                                                                                                                                                                                                 |
+====================================+=========================+=============================================================================================================================================================================================================================+
| **Server Configurations**          |                         |                                                                                                                                                                                                                             |
+------------------------------------+-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| REGISTRATION_ENABLED               | `True`                  | Set this to `True` to allow new users to sign up themselves. This setting only takes effect if the ``REGISTRATION_ENABLED`` environment setting is not `False`.                                                             |
+------------------------------------+-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Default Values**                 |                         |                                                                                                                                                                                                                             |
+------------------------------------+-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| DEFAULT_SAVE_TO_EML                | `True`                  | The default mailbox setting whether to store mails as eml.                                                                                                                                                                  |
+------------------------------------+-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| DEFAULT_SAVE_ATTACHMENTS           | `True`                  | The default mailbox setting whether to store attachments.                                                                                                                                                                   |
+------------------------------------+-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Processing Settings**            |                         |                                                                                                                                                                                                                             |
+------------------------------------+-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| THROW_OUT_SPAM                     | `True`                  | Set this to `True` to ignore emails that have a spam flag.                                                                                                                                                                  |
+------------------------------------+-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| IGNORED_MAILBOXES                  | ["Spam", "Junk"]        | List of mailboxes that are ignored when looking up mailboxes in an account."                                                                                                                                                |
+------------------------------------+-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| EMAIL_HTML_TEMPLATE                | *Omitted for space*     | The html template used to render emails to html. Uses the django template syntax and has access to all fields of the email database table. Removing template tag imports may result in a 500 responses, so be careful.      |
+------------------------------------+-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| EMAIL_CSS                          | *Omitted for space*     | The css style used to render emails to html. Refer to ``HTML_TEMPLATE`` for context on the classes.                                                                                                                         |
+------------------------------------+-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| DONT_SAVE_CONTENT_TYPE_PREFIXES    | `[""]`                  | A list of content types prefixes to not parse as attachment files. For an exhaustive list of all available MIME contenttypes see `IANA Media Types <https://www.iana.org/assignments/media-types/media-types.xhtml#text>`_. |
+------------------------------------+-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| DONT_SAVE_CONTENT_TYPE_SUFFIXES    | `[""]`                  | A list of content types suffixes to not parse as attachment files. Use this for more finegrain control than ``DONT_SAVE_CONTENT_TYPE_PREFIXES``. Plain and HTML text is always ignored as that is the bodytext.             |
+------------------------------------+-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Storage Settings**               |                         |                                                                                                                                                                                                                             |
+------------------------------------+-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| STORAGE_MAX_FILES_PER_DIR          | `10000`                 | The maximum number of files in one storage unit.                                                                                                                                                                            |
+------------------------------------+-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **API Settings**                   |                         |                                                                                                                                                                                                                             |
+------------------------------------+-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| API_DEFAULT_PAGE_SIZE (20)         | `20`                    | The default page size for paginated API response data.                                                                                                                                                                      |
+------------------------------------+-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| API_MAX_PAGE_SIZE (200)            | `200`                   | The maximum page size for paginated API response data.                                                                                                                                                                      |
+------------------------------------+-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Webapp Settings**                |                         |                                                                                                                                                                                                                             |
+------------------------------------+-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| WEB_DEFAULT_PAGE_SIZE (20)         | `20`                    | The default page size for paginated API response data.                                                                                                                                                                      |
+------------------------------------+-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| WEB_PAGE_SIZES_OPTIONS             | `[10, 25, 50, 75, 100]` | The page size options for pagination in the webapp. Should contain the ``WEB_DEFAULT_PAGE_SIZE`` value.                                                                                                                     |
+------------------------------------+-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| WEB_THUMBNAIL_MAX_DATASIZE (10 MB) | `10 MB`                 | Maximum datasize in bytes for a thumbnail in the webapp. Thumbnails larger than this will not be loaded.                                                                                                                    |
+------------------------------------+-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

If the default for one of these settings changes, your already set up instance will not be affected by that change.
To set the new default, go to the admin panel and use the reset to default option for that setting.

Robots.txt
^^^^^^^^^^

Since the rise of AI, uncounted numbers of webcrawlers are out and about online.
The robots.txt file served by many web services (including your Emailkasten instance)
is intended to tell them which pages they may access (if they care).

You can set up rules on what parts of Emailkasten crawlers are actively invited to access
and which not in the admin panel under ``Robots - Rules``.

By default all pages are allowed.
To reverse this and disallow all pages, add a rule with

- robot: `*`
- website: `your-domain.tld`
- disallowed url pattern: `/`

Security-relevant Settings
^^^^^^^^^^^^^^^^^^^^^^^^^^

Emails can contain malicious content.
Therefore security when setting up Emailkasten is of the essence.

For a secure setup:

- ``DEBUG``: Do not set this to `True` in production ever!
- ``THROW_OUT_SPAM``: Keep this setting at the default `True`
  to keep emails that have been flagged by spam-filters out of the system.
- ``IGNORED_MAILBOXES``: Add more mailbox names that typically hold the email identified as spam
  to reduce the likelihood of spam emails making it into the archive.

User Settings
-------------

The settings for individual users concern only the configuration
of the daemons they run and the mailboxes they fetch from.
They can be configured in the webapp or API directly.
Their defaults can be managed in the *Defaults* section of the admin user settings.

More details can be found in the :doc:`user manual <web-instructions>`
