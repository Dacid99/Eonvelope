Webapp Instructions
===================

Getting started
---------------

When you start Emailkasten for the first time, an admin account is created.
The username is set to ``admin`` and the password is set from the ``DJANGO_SUPERUSER_PASSWORD`` environment variable.
You should use this admin account for administrative purposes only.

To log in, open the webapp by opening the IP address of your server with the port of the application, by default ``1122``.

After you have logged in, you can make add other user accounts in the django-admin panel.


User registration
-----------------

User
^^^^

If your administrator has activated the self registration, you can register yourself via the login page

.. code::
    /users/login/

Administrator
^^^^^^^^^^^^^

You can create new users with the admin user.

To do so go to the

.. code::
    /admin

page of Emailkasten and log in if necessary.
In the ``users`` menu you can add new users to the database.


Setting up a new account
------------------------

Adding a new account
^^^^^^^^^^^^^^^^^^^^

You can add a new account at

.. code::
    /accounts/create/

which you can also reach via the button on the dashboard or the accounts page.

Fill out the form with the credentials of the account, the fields marked with a * are mandatory.
You can find the information about mailserver-URL, protocol, port in the documentation of your email provider.
The following protocols are supported:
- IMAP4
- IMAP4 over SSL
- POP3
- POP3 over SSL
-
.. note::
    If possible, use IMAP4 via SSL. This enables you to use the most features with the most security.

If you don't set the port, the default port of the protocol is used.

If you set a timeout value, the connection to the mailserver doesn't time out. As the fetching operations on the mailserver are quick and the connection is closed afterwards anyway, this setting is mostly irrelevant.

After you have added the account, you can test the configuration via the test button.
If the service is unknown, check the email server URL.
In case of a failed authentication, check the credentials.


Mailbox setup
^^^^^^^^^^^^^

When the account is set up successfully, you can collect the names of all mailboxes in the account.
You can use the fetch mailboxes button in the overview of the account or the equivalent API endpoint.
.. note::
    For POP mailaccounts, there is only a single mailbox, the 'INBOX'.

In case of success, these mailboxes will be listed in the account.
If you change a mailbox name or delete a mailbox, you can also use this method to update the mailboxes in the account. The mailbox with
You can further configure a mailbox in its detail overview.

The available settings are define how the content from the mailbox is saved.
An email can be saved in the following formats:

- .eml: This is the standard format to save email messages. If you disable this, the full original message is not archived.
- .html: The email can be processed into a html page. If you disable this, there will be no thumbnail for the emails of the mailbox.

Additionally, you can configure whether files attached to the emails are stored.

When you have decided on these settings, go ahead and test the mailbox, just like you did with the account earlier.
.. note::
    As the information about the mailbox is collected from the account itself, this should only fail if the mailbox has been deleted or renamed.

After a successful test, the option to fetch all emails in the mailbox becomes available.
Depending on the number of mailboxes this may take a while.


Daemon setup
^^^^^^^^^^^^

For every mailbox you can set up daemons that continuously query and fetch the mailboxes.
The add-daemon button on the mailbox detail page creates a new daemon configuration and lets you modify it.
Most important is the criterion setting and the period time of the daemon.

The following criteria are available:
+-------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| RECENT      | Emails that have the RECENT flag set. This flag is set to newly received emails and is removed after the first session to the mailaccount after the email has been received. Suitable if the mailbox is fetched at a high frequency.                     |
+-------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| UNSEEN      | Emails that have the UNSEEN flag set. This flag is set to newly received emails and is removed after the email has been requested by a mailclient. Suitable if the mailbox is fetched at a high frequency.                                               |
+-------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ALL         | Emails in the mailbox. Use with care.                                                                                                                                                                                                                                    |
+-------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| NEW         | Emails with RECENT and UNSEEN flag.                                                                                                                                                                                                                                      |
+-------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| OLD         | Emails that are not NEW.                                                                                                                                                                                                                                                 |
+-------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| FLAGGED     | Emails that are flagged by the user. Suitable if you want to only fetch very particular, hand-selected emails.                                                                                                                                                           |
+-------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| DRAFT       | Email drafts. Can be used to archive your drafts.                                                                                                                                                                                                                        |
+-------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| UNDRAFT     | Emails that are not drafts.                                                                                                                                                                                                                                              |
+-------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ANSWERED    | Emails that have been answered.                                                                                                                                                                                                                                          |
+-------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| UNANSWERED  | Emails that have not been answered.                                                                                                                                                                                                                                      |
+-------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| DELETED     | Emails that have been deleted. This mostly concerns the trash mailbox.                                                                                                                                                                                                   |
+-------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| UNDELETED   | Emails that have never been deleted.                                                                                                                                                                                                                                     |
+-------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| DAILY       | Emails received the last day. Ideally used with a period time of about half a day.                                                                                                                                                                                       |
+-------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| WEEKLY      | Emails received the last week. Ideally used with a period time of about half a week.                                                                                                                                                                                     |
+-------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| MONTHLY     | Emails received the last month. Ideally used with a period time of about half a month.                                                                                                                                                                                   |
+-------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ANNUALLY    | Emails received the last year. Ideally used with a period time of about half a year.                                                                                                                                                                                     |
+-------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

.. note::
    For POP accounts, only the ALL criterion is available.

.. note::
    For mailboxes with a sizeable number of emails, avoid using the ALL criterion as it will fetch all emails every time the daemon runs, causing a large workload for the server.

.. note::
    For INBOX mailboxes, the recommended setup is filtering by UNSEEN flag multiple times every minute.
    For other mailboxes, use DAILY or WEEKLY depending on the activity in the mailbox.

The cycle-period parameter defines how much time passes between two runs of the daemon.
This should be set depending on the criterion.

There are other parameters that can be changed.
- restart-time: defines how long the daemon waits before restarting after being crashed.

The logging behaviour of the daemon can be altered as well.
- log_backup_count: how many historical logfiles to store.
- logfile_size: the maximum size of a logfile.

.. note::
    The smaller the cycle-period, the larger the number of logfiles and/or the maximum size should be.

Then you can start the daemon and stop it later when required.
To troubleshoot and get information about what the daemon is doing, you can download the daemons logfile.
