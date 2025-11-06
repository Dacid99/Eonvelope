..
   SPDX-License-Identifier: CC-BY-SA 4.0

   Copyright (C) 2024 David Aderbauer & The Emailkasten Contributors
   Licensed under the Creative Commons Attribution-ShareAlike 4.0 International License.

Webapp Instructions
===================

Getting started
---------------

To log in, open the webapp by opening the IP address of your server
with the port of the application, by default ``1122``.
Emailkasten will force you to use HTTPS using its certificate, so the url must start with *https://*.

You can install Emailkasten as a progressive-webapp on your device to use it like a regular app.
The way you can do this depends on your browser.

Registration
------------

If your administrator has activated the self registration,
you can register yourself via the login page
*/users/login/*.

Alternatively you can also do so via the API.

If not, please contact your admin so they can create an user account for you.

Setting up a new mailaccount
----------------------------

Adding a new mailaccount
^^^^^^^^^^^^^^^^^^^^^^^^

You can add a new mailaccount at */accounts/create/*, which you can also reach via the button on the dashboard or the accounts page.

Fill out the form with the credentials of the account, the fields marked with a * are mandatory.
In case you have set up two-factor-authentication for your mailaccount,
you need an app-password (can be created in the settings of your email account)
in lieu of a your plain password.
You can find the information about mailserver-URL, protocol, port in the documentation
of your email provider.
The following protocols are supported:

- IMAP4
- IMAP4 (unencrypted)
- POP3
- POP3 (unencrypted)
- Microsoft Exchange

.. note::
    If possible, use IMAP4 via SSL.
    This enables you to use the most features with the most security.

.. note::
    Please do not use the unencrypted version unless all other options fail.
    They are only implemented for backward compatibility.

The mailserver URL does not need to feature a protocol,
the (sub)domain name is fine e.g. *imap.mydomain.tld*.
If you don't set the mailserver port, the default port of the protocol is used.

.. note::
    If you use Exchange you can specify a full URL path starting with http(s):// to the service endpoint as mailserver-URL.
    In that case the port setting is not used as the port should already be part of that URL.

If you don't set a timeout value when using IMAP and POP,
the connection to the mailserver doesn't time out.
That is the intended behaviour as the fetching of emails is quick
and the connection is closed afterwards anyway.

For Exchange this setting behaves a bit differently.
Setting a value enables a retry and faulttolerance logic timing out after the given value.
It is encouraged to use this option with a value of a few seconds
to reduce random connection errors.
Don't use larger values as this may significantly impact
the runtime of individual requests to the server.

After you have added the account, you can test the configuration via the test button.
If the service is unknown, check the email server URL.
In case of a failed authentication, check the credentials.


Mailbox setup
^^^^^^^^^^^^^

When the account is set up successfully, you can collect the names of all mailboxes in the mailaccount.
You can use the fetch mailboxes button in the overview of the account
or the equivalent API endpoint.

.. note::
    For POP mailaccounts, there is only a single mailbox, the 'INBOX'.

In case of success, these mailboxes will be listed in the account.
Depending on the settings made by your admin, not all mailboxes in your account may be present.
By default, mailboxes for spammails are excluded to avoid archiving malicious content.

If you change a mailbox name or create a new one, you can also use this method
to update the mailboxes in the account.

You can further configure a mailbox in its detail overview.

The available settings are define how the contents from the mailbox are saved.
By default, the emails will be stored as .eml files.
If you disable this, the full original message is not archived.

Additionally, you can configure whether files attached to the emails are stored.
By default they will be saved.

When you have decided on these settings, go ahead and test the mailbox,
just like you did with the account earlier.

.. note::
    As the information about the mailbox is collected from the account itself,
    this should only fail if the mailbox has been deleted or renamed.

After a successful test, the option to fetch all emails in the mailbox becomes available.
Depending on the number of mailboxes this may take a while.

.. note::
    The Exchange protocol is especially sluggish in accessing emails.
    Please do not try to fetch more than 25 messages at once.
    Doing so most certainly leads to a timeout and an error.


Routine setup
^^^^^^^^^^^^^

For every mailbox you can set up routines that continuously query and fetch the mailboxes.
The add-routine button on the mailbox detail page creates a new routine configuration
and lets you modify it.
Most important is the criterion setting and the period time of this routine.

The following criteria are available:

+-------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| RECENT      | Emails that have the RECENT flag set. This flag is set to newly received emails and is removed after the first session to the mailaccount after the email has been received. Suitable if the mailbox is fetched at a high frequency.                                     |
+-------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| UNSEEN      | Emails that have the UNSEEN flag set. This flag is set to newly received emails and is removed after the email has been requested by a mailclient. Suitable if the mailbox is fetched at a high frequency.                                                               |
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
    The most precise time-based lookup is DAILY as IMAP does only support lookup by date, not by timestamp.

.. note::
    For a complete coverage of all emails that enter and exit a mailaccount,
    set up a routine for both the INBOX and the Sent mailbox.
    That way you can make use of Emailkasten's feature to capture, archive and map complete conversations.
    Additionally you can archive your drafts by fetching that mailbox repeatedly.

.. note::
    For mailboxes with a sizeable number of emails (e.g. because you rarely clean out your INBOX),
    avoid using the ALL criterion as it will fetch all emails every time the routine runs,
    causing a large workload for the server.

.. note::
    For INBOX mailboxes, the recommended setup is filtering by UNSEEN flag multiple times every minute.
    For other mailboxes, use DAILY or WEEKLY depending on the activity in the mailbox.

.. note::
    If you use a different emailarchive server as backup, you may not be able to use filtering by RECENT or UNSEEN,
    since that may lead to race conditions between the two servers.
    Just use the time-based filters instead.
    Emailkasten with IMAP safely opens the mailbox in read-only mode, so no flags are altered.

The *interval-period* setting defines the time unit that lies between two routine jobs runs.
The *interval-every* parameter defines
how much many *interval-period*'s pass between two runs of the routine job.
This should be set depending on the criterion.

There are other parameters that can be changed.

- restart-time: defines how long the routine waits before restarting after being crashed.

.. note::
    The smaller the cycle-period, the larger the number of logfiles and/or the maximum size should be.

The routine is automatically started when you save it, but runs the first time only after one cycle-period.
If you want it to run right away, you can use the test action in the menu, which triggers a single run.
You can also stop it at any time if necessary.

To troubleshoot and get information about what the routine is doing,
check the last error message of the routine and attempt a test run.
If the issue lies with the mailbox or account that the routine is fetching from, they will be marked as unhealthy as well.


Archived data
-------------

Once data from your emails has been collected and archived, you can view it using the web interface.

Emailkasten gathers data about three types of information in your emails. Attachments, correspondents and of course the emails themselves.

Each of these can be search and filtered by various criteria. Every single item can be viewed individually as well.
Items that are important to you can marked as favorites. Just click the star icon in the card of the item to toggle the favorite status.
Favorite items are sorted to the top of lists so they are easily found.

Tables and lists
""""""""""""""""

You can get an overview of your data in two formats: listed or tabular.

The listed format presents a series of cards representing the data
while the tabular interface gives you a clean table with information with each object in its own row.

The table interface can always be found by appending `table/` to the url of the corresponding list overview.

Emails
^^^^^^

For IMAP and Exchange email accounts, emails can be restored to the mailbox that they were found in.

Conversations
"""""""""""""

Emails contains headers linking them with other emails.
Using this data allows Emailkasten to reconstruct complete conversations, given that all emails in it are present.
Otherwise the conversations may only be fragmentary.
We try to make sure to fetch emails in the correct chronological order to be able to resolve all links.
Nonetheless it may happen that a single fetch of many connected mails does not find all conversations.
The safest way to allow this feature to play out is to set up routines both for you INBOX and OUTBOX mailboxes,
that fetch multiple times a day, as described above.

Timeline overview
"""""""""""""""""

For emails there are additional special listing pages.
These allow you to view your archived emails in chronological order.

You can see the emails received within a specific timeframe
that can be chosen from specific days to entire year.

Select the timespan you are interested in and the emails from that period of time will be listed for you.
If you wish you can then make the timeframe more fine-grain and get an even better history of your mail traffic and activity.

Individual emails can be downloaded in eml format, if they were saved as such.


Attachments
^^^^^^^^^^^

If you have set up third-party services in your profile, you can share them with these services.

Like emails, attachments can be downloaded, if they were archived as files.


Correspondents
^^^^^^^^^^^^^^

Correspondents can be downloaded as vcard files with emailaddress and name inside.
This file can be imported to other digital contacts and addressbooks.



Import and Export
-----------------

Import
^^^^^^

Instead of fetching the emails from a mailaccount, you can also import emails in various file formats.
The import adds the messages to a mailbox of your choice, the upload option can be found on the detail page of the mailbox.

The following formats are supported:

+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| .eml           | Standard email format, holds a single message.                                                                                                                                         |
+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| .zip[.eml]     | A zipfile holding multiple .eml files with single messages in each of them.                                                                                                            |
+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| .mbox          | Format for multiple emails, common for multi-file exports from mailclients, especially on UNIX systems.                                                                                |
+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| .babyl         | Format for multiple emails, used by the Rmail mail user agent included with Emacs                                                                                                      |
+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| .mmdf          | Format for multiple emails, invented for the Multichannel Memorandum Distribution Facility, a mail transfer agent.                                                                     |
+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| .zip[.mh]      | Directory-based format for multiple emails, used by the MH Message Handling System mail agent. The MH mailbox has to be given in zipped form.                                          |
+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| .zip[.maildir] | Directory-based format for multiple emails, initiated by the qmail mail transfer agent and now widely supported by other programs. The Maildir mailbox has to be given in zipped form. |
+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

.. note::
    The maildir format must contains a complete mailstorage in the zipfile.
    The structure inside the .zip needs to be similar to
    ::
       /
       └── maildir
           ├── cur
           ├── new
           │   ├── mail-1
           |   ...
           |   └── mail-2
           |
           └── tmp

.. note::
    The mh format must contain a .mh-sequences file, even if its empty.
    The structure inside the .zip needs to be similar to
    ::
       /
       └── mh
           ├── 1
           ├── 2
           └── .mh_sequences

If you are unsure what structure inside the zipfile is required for a successful upload,
try exporting emails in that same format.
The structure of the file you will receive is the same structure required for import.

If you have a file in a proprietary format like .msg or .ost,
please convert it to one of the upper formats using a conversion tool,
plenty of these are available on github and other platforms.

You can also import data in various tabular formats into the database via the admin panel.


Export
^^^^^^

Exporting can be done either by downloading entire mailboxes via the download option on the mailbox item page
or by handpicking and downloading these emails in a bunch.
The second option is currently only available via the API.
Please refer to the :doc:`API documentation for instructions <api-instructions>` on the usage of these endpoints.
The same formats as above are accepted.

You can also export data from the database in various tabular formats via the admin panel.
The supported formats are csv, xls, xlsx, tsv, ods, json, yaml, html.
