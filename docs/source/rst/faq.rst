..
   SPDX-License-Identifier: CC-BY-SA 4.0

   Copyright (C) 2024 David Aderbauer & The Eonvelope Contributors
   Licensed under the Creative Commons Attribution-ShareAlike 4.0 International License.

FAQ
===

This is a list of frequently asked questions with their answers
and quick solutions to common problems.


I am new to self-hosting, how can I set up an instance the easiest?
-------------------------------------------------------------------

Setting up an Eonvelope server is quick and straightforward.
The simplest path is described on :doc:`the quickstart page <quickstart>`.


Do I need special hard- or software to run Eonvelope?
-------------------------------------------------------

One goal of this project is to be easily available across many platforms.
Essentially, everything that can run containers is viable to deploy Eonvelope.
That includes every modern Linux, Windows, MacOS, FreeBSD, etc.


Do I need a license to use this application?
--------------------------------------------

This project is licensed under the :doc:`AGPLv3 license <license>`.
That means that everyone can freely use this software.

There is only a restriction if you want to alter and publish the source code.
In that case your version of the program has to be released under the same license,
so the project remains free software.


I can't access my instance using the port I assigned to it.
-----------------------------------------------------------

Eonvelope is served exclusively over https. Please make sure that the URL you use starts with https://.
Perhaps you are trying to access Eonvelope via an address that is not in the ALLOWED_HOSTS docker environment variable.
If none of these fixes work, please check the logs to see if the webserver (gunicorn) in the container has trouble starting.
Its logs should give you a hint of what is going on.


After setting up my instance, I don't know how to sign up or log in.
--------------------------------------------------------------------

You can login with the default admin account, which is automatically created.
The credentials are `admin` and the `DJANGO_SUPERUSER_PASSWORD` that you set in the docker-compose file.
Using this account and the admin interface, you can create other users.
If users should be able to sign up themselves, set `REGISTRATION_ENABLED` to `True`.
More details are available on the :doc:`installation page <installation>`.


I can't access my Eonvelopes webapp, I always land on the no internet connection page.
--------------------------------------------------------------------------------------

This can happen if you have the PWA offline page cached and have not yet accepted the self-signed certificate.
Open your browsers developer bar and delete all files cached by django-pwa. 
Now when you refresh, you should be prompted to accept the certificate.
To solve this issue long-term, reverse-proxy your instance.


If I delete an account in Eonvelope, does that delete the account on the mailserver too?
------------------------------------------------------------------------------------------

No, only the data in the Eonvelope database will be deleted.
Eonvelope will never destroy data on your mailserver!


I have found a problem with the application, what should I do?
--------------------------------------------------------------

Please try to figure out whether the problem may be specific for your setup first.
If it is not, please file an issue in one of the online repositories.

In case the problem is not related to the source code itself,
there is unfortunately not much we can do about it.
Please try to debug it with other users and admins over stack-overflow, reddit or other platforms.

If the problem is security-related please contact one of the developers privately instead.


My language is missing in the translations, can I help to add it?
-----------------------------------------------------------------

Yes of course, we are always happy to include new languages!

Translation is done via `weblate <https://hosted.weblate.org/projects/eonvelope/>`_.
To get a quickstart look at :doc:`the translations instruction <translations>`.
If your language is also missing on `weblate <https://hosted.weblate.org/projects/eonvelope/>`_,
please file an issue using the missing-language template.


Parts of the user interface are not accessible on my device, what can I do?
---------------------------------------------------------------------------

It is important to us that everyone can use Eonvelope with as few barriers as possible.

If you find a part of the frontend that lacks accessibility or is confusing or flawd in this regard
please don't hesitate to let us know via an issue using the missing-accessibility template.


How can I contribute to this project?
-------------------------------------

Everyone is welcome to help with the development of Eonvelope!

To get you off to a good start please check out the quickstart and codestyle guidelines.
You can find them alongside the source code documentation in the :doc:`developers section <developers>`.
