..
   SPDX-License-Identifier: CC-BY-SA 4.0

   Copyright (C) 2024 David Aderbauer & The Eonvelope Contributors
   Licensed under the Creative Commons Attribution-ShareAlike 4.0 International License.

Admin Instructions
==================

This is a collection of guidelines for the Eonvelope admin user and the server admin.
Typically that will be one an the same person.

When you start Eonvelope for the first time, an admin user account is created.
The username is set to ``admin`` and the password
is set from the ``DJANGO_SUPERUSER_PASSWORD`` environment variable.
You should use this account for administrative purposes only.

This document focuses on management tasks after setup of the Eonvelope instance.
Information for the setup can found in the pages about :doc:`installation <installation>`.


Management tasks
----------------

Add user
^^^^^^^^

If registration is disabled, the only way to add new users is via the admin panel.
Go to the users section and use the add function.

Generate API token for a user
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Every user can have a persistent token for authentication to the Eonvelope API.
These are generated in the token section of the admin panel.
Tokens can also be deleted there.

Forgotten username
^^^^^^^^^^^^^^^^^^

In case a user forgets their username for login, the admin user can just look it up via the admin panels user section.

.. note::
    It is not possible to forget the username of the admin, it is always ``admin``.


Forgotten password
^^^^^^^^^^^^^^^^^^

If a user has forgotten their password, a new one can be set for them via the admin panels *user* interface.
The user may change it himself once logged in.

Admin password forgotten
""""""""""""""""""""""""

If the admin user password has been forgotten, there are a variety of options.

If the admin password has not been changed, you can just look it up in the ``docker-compose.yml`` environmental variables.

If you have access to the docker management, you can use ``docker exec`` to run

.. code-block::
    python3 manage.py changepassword admin

and change the password.

Alternatively, you can create another admin account by running

.. code-block:: bash

    docker exec -it eonvelope-web python3 manage.py createsuperuser --username=rescueadmin --email=  --noinput

in the servers terminal.
This ``rescueadmin`` account can be accessed with the password from the ``docker-compose.yml``.

Using this account you can reset the password just like with a regular user.
You may delete this additional admin afterwards. You can recreate it if required.


MFA activated, device lost, no recovery codes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If a user has MFA activated but lost their device and all recovery codes, you can look into the database via the admin panel.
The second factor secrets are stored in the mfa table. The secret for authentication can be found in the TOTP entry for the locked-out user.
Take that secret and supply it to the user so they can set up the authenticator app on their device.
They should turn MFA off and back on again afterwards to change the now compromised secret.

.. note::
    If the admin users MFA is lost, you can perform the same recovery by creating a second admin account as described :ref:`Admin password forgotten <above>`.

Delete user
^^^^^^^^^^^

Users can be deleted the same way they are created, using the admin panels user pages.

Configurations
--------------

As admin user you can change instance-wide configurations via the admin panel.
The settings can be found and changed under the 'constance' header.

The server admin can configure the application via the docker environmental variables.

See and :doc:`configuration <configuration>` for more details.



Robots.txt
----------

Since the rise of AI, uncounted numbers of webcrawlers are out and about online.
The robots.txt file served by many web services (including your Eonvelope instance)
is intended to tell them which pages they may access (if they care).

You can set up rules on what parts of Eonvelope crawlers are actively invited to access
and which not in the admin panel under ``Robots - Rules``.

By default all pages are allowed.
To reverse this and disallow all pages, add a rule with

- robot: `*`
- website: `your-domain.tld`
- disallowed url pattern: `/`
