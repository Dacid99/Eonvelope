..
   SPDX-License-Identifier: CC-BY-SA 4.0

   Copyright (C) 2024 David Aderbauer & The Eonvelope Contributors
   Licensed under the Creative Commons Attribution-ShareAlike 4.0 International License.

Configuration
=============

The configuration for Eonvelope is divided into 3 levels:

- *Server admin*: Can only be changed by the server admin hosting the Eonvelope instance
- *Admin user*: Can only be changed by an admin or staff user in the Eonvelope instance
- *Any user*: Can be changed by and for any individual user

The more people have access to the settings, the less security-relevant they are.

**All settings have reasonable and safe defaults.**

Server Admin Settings
---------------------

These settings are stored in environmental variables
that can be adapted via the *docker-compose.yml* file.

You can check out the docker-compose files in the repository for further reference.

Mandatory
^^^^^^^^^

+---------------------------+--------------------------------------------------------------------------------------+
| Setting                   | Description                                                                          |
+===========================+======================================================================================+
| SECRET_KEY                | A random string, the longer the better.                                              |
|                           | This is the heart of Django's cryptographic functionalities so set it and forget it! |
+---------------------------+--------------------------------------------------------------------------------------+
| DATABASE                  | The name of the database for Eonvelope.                                              |
|                           | Must match the ``MARIADB_DATABASE`` value of the MariaDB config.                     |
+---------------------------+--------------------------------------------------------------------------------------+
| DATABASE_USER             | The username for the DB.                                                             |
|                           | Must match the ``MARIADB_USER`` value of the MariaDB config.                         |
+---------------------------+--------------------------------------------------------------------------------------+
| DATABASE_PASSWORD         | The user's password for the DB.                                                      |
|                           | Must match the ``MARIADB_PASSWORD`` value of the MariaDB config.                     |
+---------------------------+--------------------------------------------------------------------------------------+
| DJANGO_SUPERUSER_PASSWORD | The password of the Eonvelope admin user that is created by default.                 |
|                           | Pick a secure password and keep it safe.                                             |
|                           | Access to the admin allows access to the database so this must be kept secure.       |
+---------------------------+--------------------------------------------------------------------------------------+
| ALLOWED_HOSTS             | The hostnames that the application is served from as a comma separated list.         |
|                           | Select this restrictively, it guards against man-in-the-middle type attacks.         |
|                           | *localhost* is always included.                                                      |
+---------------------------+--------------------------------------------------------------------------------------+

Optional
^^^^^^^^

+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| Setting                           | Default     | Description                                                                                                               |
+===================================+=============+===========================================================================================================================+
| SLIM                              | *False*     | Set this to `True` if you run Eonvelope on a system with sparse resources.                                                |
|                                   |             | In slim mode, some plugins will not be loaded and thus less resources will be used.                                       |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| DATABASE_TYPE                     | *mysql*     | The type of database that is used.                                                                                        |
|                                   |             | Possible values are mysql, postgresql and sqlite3.                                                                        |
|                                   |             | Must match the database type of the db container.                                                                         |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| APP_LOG_LEVEL                     | *INFO*      | The log level of the Eonvelope logger.                                                                                    |
|                                   |             | It logs to Eonvelope.log in the logs docker volume                                                                        |
|                                   |             | and contains information about events in the Eonvelope application components.                                            |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| DJANGO_LOG_LEVEL                  | *INFO*      | The log level of the Django logger.                                                                                       |
|                                   |             | It logs to django.log in the logs docker volume                                                                           |
|                                   |             | and contains information about events in the Django components.                                                           |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| CELERY_LOG_LEVEL                  | *INFO*      | The log level of the logger for celery.                                                                                   |
|                                   |             | It logs to only to celery.log in the logs docker volume                                                                   |
|                                   |             | and contains information about events in the celery event queue.                                                          |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| AMQP_LOG_LEVEL                    | *INFO*      | The log level of the logger for amqp components.                                                                          |
|                                   |             | It logs only to amqp.log in the logs docker volume                                                                        |
|                                   |             | and contains information about events in the rabbitmq messagebroker.                                                      |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| LOGFILE_MAXSIZE                   | *10485760*  | The maximum size for a single log file in bytes.                                                                          |
|                                   |             | This should not be too large so the log files can be read with a standard editor.                                         |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| LOGFILE_BACKUP_NUMBER             | *5*         | The number of log files to keep in the backstack.                                                                         |
|                                   |             | This number should be higher the lower your log level.                                                                    |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| REGISTRATION_ENABLED              | *False*     | Set this to `True` to allow self-sign-on.                                                                                 |
|                                   |             | Set this to `False`, if you never want users to sign up themselves, so only staff members can create new users.           |
|                                   |             | If True, the admin level ``REGISTRATION_ENABLED`` setting becomes active.                                                 |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| GUNICORN_WORKER_NUMBER            | *1*         | The number of worker processes serving the webpages.                                                                      |
|                                   |             | For better load balancing set this to 2-4 * NUM_CORES,                                                                    |
|                                   |             | as recommended by the `gunicorn docs <https://docs.gunicorn.org/en/stable/settings.html#workers>`                         |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| STRICT_PASSWORDS                  | *True*      | Set this to `True` to have user passwords strictly validated for length, commonness and simplicity.                       |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| DEBUG                             | *False*     | Set this to `True` to run the application in debug mode.                                                                  |
|                                   |             | Do not activate this unless you're trying to debug an issue and are not exposing the debug instance.                      |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| ENABLE_FLOWER                     | *False*     | Set this to `True` to run a flower interface for managing background tasks in the Eonvelope server.                       |
|                                   |             | If you want to use this, you also need to map port 5555 in your docker-compose.yml file.                                  |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| DISALLOWED_USER_AGENTS            |             | Regex patterns for user agents that must not visit any page of this Eonvelope instance, as a comma separated list.        |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| CSRF_TRUSTED_ORIGINS              |             | All URLs that are trusted with unsafe requests, as a comma separated list.                                                |
|                                   |             | Must start with a scheme like *http://* or *https://*.                                                                    |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| CSRF_COOKIE_AGE                   | *31449600*  | The validity lifetime of the csrf cookie in seconds.                                                                      |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| CSRF_COOKIE_SAMESITE              | *Lax*       | The samesite value on the csrf cookie.                                                                                    |
|                                   |             | See https://docs.djangoproject.com/en/5.1/ref/settings/#session-cookie-samesite for more info.                            |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| CACHE_MIDDLEWARE_SECONDS          | *600*       | The timespan in seconds for which a page is cached by the instance.                                                       |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| SECURE_HSTS_SECONDS               | *31536000*  | The HSTS timespan in seconds.                                                                                             |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| LANGUAGE_COOKIE_AGE               | *2419200*   | The validity lifetime of the language cookie in seconds.                                                                  |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| LANGUAGE_COOKIE_SAMESITE          | *None*      | The samesite value on the language cookie.                                                                                |
|                                   |             | See https://docs.djangoproject.com/en/5.1/ref/settings/#session-cookie-samesite for more info.                            |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| SESSION_COOKIE_AGE                | *2419200*   | The validity lifetime of the session cookie in seconds.                                                                   |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| SESSION_EXPIRE_AT_BROWSER_CLOSE   | *False*     | Set this to `True` to close all sessions when the browser closes.                                                         |
|                                   |             | This will force users to login every time they start a new browser session.                                               |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| SESSION_COOKIE_SAMESITE           | *Lax*       | The samesite value on the session cookie.                                                                                 |
|                                   |             | See https://docs.djangoproject.com/en/5.1/ref/settings/#session-cookie-samesite for more info.                            |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| ACCOUNT_LOGIN_TIMEOUT             | *900*       | The maximum allowed time (in seconds) for a login to go through the various login stages.                                 |
|                                   |             | This limits, for example, the time span that the MFA stage remains available.                                             |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| ACCOUNT_USERNAME_BLACKLIST        | *[]*        | A list of usernames that are forbidden.                                                                                   |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| ACCOUNT_USERNAME_MIN_LENGTH       | *1*         | The minimum allowed length of a username.                                                                                 |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| ACCOUNT_SESSION_REMEMBER          |             | Leave unset to ask the user (“Remember me?”) or set `False` to never remember, and `True` to always remember.             |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE | *False*     | Whether or not the user is automatically logged out after changing or setting their password.                             |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| ACCOUNT_REAUTHENTICATION_TIMEOUT  | *300*       | If successful (re)authentication happened within this amount of seconds, new reauthentication flows are silently skipped. |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| ACCOUNT_REAUTHENTICATION_REQUIRED | *False*     | Whether or not reauthentication is required before the user can alter his account.                                        |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| USERSESSIONS_KEEP_UPDATED         | *True*      | Whether or not user sessions are kept updated.                                                                            |
|                                   |             | Enabling this setting makes sure that the usersession is kept track of,                                                   |
|                                   |             | meaning the IP address, user agent and last seen timestamp are all kept up to date.                                       |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| MFA_TOTP_ISSUER                   | *Eonvelope* | The issuer appearing in the MFA TOTP QR code.                                                                             |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| MFA_TOTP_TOLERANCE                | *1*         | The timespan after expiration in seconds during which the old MFA code is still accepted.                                 |
|                                   |             | Smaller values are more secure, but more likely to fail due to clock drift.                                               |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| MFA_TOTP_PERIOD                   | *30*        | The period that a MFA TOTP code will be valid for, in seconds.                                                            |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| MFA_TOTP_DIGITS                   | *6*         | The number of digits for MFA TOTP codes.                                                                                  |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| MFA_RECOVERY_CODE_COUNT           | *10*        | The number of MFA recovery codes.                                                                                         |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| MFA_RECOVERY_CODE_DIGITS          | *8*         | The number of digits of each MFA recovery code.                                                                           |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| MFA_TRUST_ENABLED                 | *True*      | Set this to `False` to disable the 'trust browser' functionality.                                                         |
|                                   |             | This will force users that have MFA configured to always enter a MFA code on login.                                       |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| MFA_TRUST_COOKIE_AGE              | *2419200*   | The validity lifetime of the trust-browser cookie, in seconds.                                                            |
|                                   |             | For this time interval, MFA is skipped for this browser instance.                                                         |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+
| MFA_TRUST_COOKIE_SAMESITE         | *Lax*       | The samesite value on the trust-browser cookie.                                                                           |
|                                   |             | See https://docs.djangoproject.com/en/5.1/ref/settings/#session-cookie-samesite for more info.                            |
+-----------------------------------+-------------+---------------------------------------------------------------------------------------------------------------------------+


Admin User Settings
-------------------

These settings can be found and managed in the Django admin interface at */admin* under *constance - Configuration*.
They are sorted into categories:

+------------------------------------+-------------------------+---------------------------------------------------------------------------------------------------+
| Setting                            | Default                 | Description                                                                                       |
+====================================+=========================+===================================================================================================+
| **Server Configurations**          |                         |                                                                                                   |
+------------------------------------+-------------------------+---------------------------------------------------------------------------------------------------+
| REGISTRATION_ENABLED               | *True*                  | Set this to `True` to allow new users to sign up themselves.                                      |
|                                    |                         | This setting only takes effect if the ``REGISTRATION_ENABLED`` environment setting is not `False`.|
+------------------------------------+-------------------------+---------------------------------------------------------------------------------------------------+
| **Default Values**                 |                         |                                                                                                   |
+------------------------------------+-------------------------+---------------------------------------------------------------------------------------------------+
| DEFAULT_SAVE_TO_EML                | *True*                  | The default mailbox setting whether to store mails as eml.                                        |
+------------------------------------+-------------------------+---------------------------------------------------------------------------------------------------+
| DEFAULT_SAVE_ATTACHMENTS           | *True*                  | The default mailbox setting whether to store attachments.                                         |
+------------------------------------+-------------------------+---------------------------------------------------------------------------------------------------+
| DEFAULT_INBOX_INTERVAL_EVERY       | *30*                    | The default number of periods between two runs of a standard routine for a SENT mailbox.          |
+------------------------------------+-------------------------+---------------------------------------------------------------------------------------------------+
| DEFAULT_INBOX_FETCHING_CRITERION   | *UNSEEN*                | The default fetching criterion for a standard routine for a INBOX mailbox.                        |
|                                    |                         | If you select a criterion that is not available for an account, the default is used instead.      |
+------------------------------------+-------------------------+---------------------------------------------------------------------------------------------------+
| DEFAULT_SENTBOX_INTERVAL_EVERY     | *1*                     | The default number of periods between two runs of a standard routine for a SENT mailbox.          |
+------------------------------------+-------------------------+---------------------------------------------------------------------------------------------------+
| DEFAULT_SENTBOX_FETCHING_CRITERION | *DAILY*                 | The default fetching criterion for a standard routine for a SENT mailbox.                         |
|                                    |                         | If you select a criterion that is not available for an account, the default is used instead.      |
+------------------------------------+-------------------------+---------------------------------------------------------------------------------------------------+
| **Processing Settings**            |                         |                                                                                                   |
+------------------------------------+-------------------------+---------------------------------------------------------------------------------------------------+
| THROW_OUT_SPAM                     | *True*                  | Set this to `True` to ignore emails that have a spam flag.                                        |
+------------------------------------+-------------------------+---------------------------------------------------------------------------------------------------+
| IGNORED_MAILBOXES_REGEX            | *(Spam|Junk)*           | Regex pattern (case-insensitive) for mailbox names                                                |
|                                    |                         | that are ignored when looking up mailboxes in an account.                                         |
+------------------------------------+-------------------------+---------------------------------------------------------------------------------------------------+
| EMAIL_HTML_TEMPLATE                | *Omitted for space*     | The html template used to render emails to html.                                                  |
|                                    |                         | Uses the django template syntax and has access to all fields of the email database table.         |
|                                    |                         | Removing template tag imports may result in a 500 responses, so be careful.                       |
+------------------------------------+-------------------------+---------------------------------------------------------------------------------------------------+
| EMAIL_CSS                          | *Omitted for space*     | The css style used to render emails to html.                                                      |
|                                    |                         | Refer to ``HTML_TEMPLATE`` for context on the classes.                                            |
+------------------------------------+-------------------------+---------------------------------------------------------------------------------------------------+
| DONT_PARSE_CONTENT_MAINTYPES       | *[""]*                  | A list of content maintypes to not parse as attachment files.                                     |
|                                    |                         | For an exhaustive list of all available MIME contenttypes                                         |
|                                    |                         | see `IANA Media Types <https://www.iana.org/assignments/media-types/media-types.xhtml#text>`_.    |
+------------------------------------+-------------------------+---------------------------------------------------------------------------------------------------+
| DONT_PARSE_CONTENT_SUBTYPES        | *[""]*                  | A list of content subtypes to not parse as attachment files.                                      |
|                                    |                         | Use this for more finegrain control than ``DONT_SAVE_CONTENT_TYPE_PREFIXES``.                     |
|                                    |                         | Plain and HTML text is always ignored as that is the bodytext.                                    |
+------------------------------------+-------------------------+---------------------------------------------------------------------------------------------------+
| **Storage Settings**               |                         |                                                                                                   |
+------------------------------------+-------------------------+---------------------------------------------------------------------------------------------------+
| STORAGE_MAX_FILES_PER_DIR          | *10000*                 | The maximum number of files in one storage unit.                                                  |
+------------------------------------+-------------------------+---------------------------------------------------------------------------------------------------+
| **API Settings**                   |                         |                                                                                                   |
+------------------------------------+-------------------------+---------------------------------------------------------------------------------------------------+
| API_DEFAULT_PAGE_SIZE              | *20*                    | The default page size for paginated API response data.                                            |
+------------------------------------+-------------------------+---------------------------------------------------------------------------------------------------+
| API_MAX_PAGE_SIZE                  | *200*                   | The maximum page size for paginated API response data.                                            |
+------------------------------------+-------------------------+---------------------------------------------------------------------------------------------------+
| **Webapp Settings**                |                         |                                                                                                   |
+------------------------------------+-------------------------+---------------------------------------------------------------------------------------------------+
| WEB_DEFAULT_PAGE_SIZE              | *20*                    | The default page size for paginated API response data.                                            |
+------------------------------------+-------------------------+---------------------------------------------------------------------------------------------------+
| WEB_PAGE_SIZES_OPTIONS             | *[10, 25, 50, 75, 100]* | The page size options for pagination in the webapp.                                               |
|                                    |                         | Should contain the ``WEB_DEFAULT_PAGE_SIZE`` value.                                               |
+------------------------------------+-------------------------+---------------------------------------------------------------------------------------------------+
| WEB_THUMBNAIL_MAX_DATASIZE         | *10 MB*                 | Maximum datasize in bytes for a thumbnail in the webapp.                                          |
|                                    |                         | Thumbnails larger than this will not be loaded.                                                   |
+------------------------------------+-------------------------+---------------------------------------------------------------------------------------------------+

If the default for one of these settings changes, your already set up instance will not be affected by that change.
To set the new default, go to the admin panel and use the reset to default option for that setting.

Over time old settings that are no longer used by the application may accumulate in the database.
If you wish to get rid of them, you can run the following command in your servers terminal.

.. code-block:: bash

  docker exec -it eonvelope-web python3 manage.py constance remove_stale_keys



Security-Relevant Settings
^^^^^^^^^^^^^^^^^^^^^^^^^^

Emails can contain malicious content.
Therefore security when setting up Eonvelope is of the essence.

For a secure setup:

- ``DEBUG``: Do not set this to `True` in production ever!
- ``THROW_OUT_SPAM``: Keep this setting at the default `True`
  to keep emails that have been flagged by spam-filters out of the system.
- ``IGNORED_MAILBOXES_REGEX``: Add more mailbox names that typically hold the email identified as spam
  to reduce the likelihood of spam emails making it into the archive.

User Settings
-------------

The users have separate settings that they can configure via their profile page.
These settings mostly concern third-party integrations.

+------------------------+---------------------------------------------------------------------------------------------+
| Setting                | Description                                                                                 |
+------------------------+---------------------------------------------------------------------------------------------+
| Paperless-URL          | The URL of the Paperless-ngx server that the user wants to share attachments with.          |
+------------------------+---------------------------------------------------------------------------------------------+
| Paperless-API-Key      | The users API key to the upper Paperless-ngx server.                                        |
+------------------------+---------------------------------------------------------------------------------------------+
| Paperless-Tika-enabled | Whether the Paperless-ngx server has Tika enabled for additional filetype support.          |
+------------------------+---------------------------------------------------------------------------------------------+
| Immich-URL             | The URL of the Paperless-ngx server that the user wants to share attachments with.          |
+------------------------+---------------------------------------------------------------------------------------------+
| Immich-API-Key         | The users API key to the upper Paperless-ngx server.                                        |
+------------------------+---------------------------------------------------------------------------------------------+
| Nextcloud-URL          | The URL of the Nextcloud server that the user wants to share data with.                     |
+------------------------+---------------------------------------------------------------------------------------------+
| Nextcloud-Username     | The users Nextcloud account username.                                                       |
+------------------------+---------------------------------------------------------------------------------------------+
| Nextcloud-Password     | The users Nextcloud account password or app-password.                                       |
+------------------------+---------------------------------------------------------------------------------------------+
| Nextcloud-Addressbook  | The name of the Nextcloud addressbook that the user wants to share correspondent data with. |
|                        | Defaults to `contacts` the default Nextcloud addressbook.                                   |
+------------------------+---------------------------------------------------------------------------------------------+


More details can be found in the :doc:`integrations page<integrations>`.

There are some more user-defined settings to configure the behaviour of individual objects like mailboxes and routines.
You can read about them in the :doc:`user manual<web-instructions>`.
