Troubleshooting
===============

This is a curated list of issues that may arise when hosting or using Eonvelope.


I can't access my instance using the port I assigned to it.
-----------------------------------------------------------

Eonvelope is served exclusively over https. Please make sure that the URL you use starts with https://.

Perhaps you are trying to access Eonvelope via an address that is not in the ALLOWED_HOSTS docker environment variable.

If none of these fixes work, please check the logs to see if the webserver (gunicorn) in the container has trouble starting.
Its logs should give you a hint of what is going on.


I can't access my Eonvelopes webapp, I always land on the no internet connection page.
--------------------------------------------------------------------------------------

This can happen if you have the PWA offline page cached and have not yet accepted the self-signed certificate.
Open your browsers developer bar and delete all files cached by django-pwa.
Now when you refresh, you should be prompted to accept the certificate.
To solve this issue long-term, reverse-proxy your instance.


After setting up my instance, I don't know how to sign up or log in.
--------------------------------------------------------------------

You can login with the default admin account, which is automatically created.
The credentials are `admin` and the `DJANGO_SUPERUSER_PASSWORD` that you set in the docker-compose file.
Using this account and the admin interface, you can create other users.
If users should be able to sign up themselves, set `REGISTRATION_ENABLED` to `True`.
More details are available on the :doc:`installation page <installation>`.


I have locked myself out of my Eonvelope account.
-------------------------------------------------

This is a job for the admin, go to :doc:`the admin instructions <admin-instructions>`,
where there is a list of instructions for different lockout scenarios.


I am using the API and some name(s) and(/or) behavior(s) don't make sense to me.
---------------------------------------------------------------------------------

This may be because that field have been renamed or may have no analogue in the web interface.

There is a list with these known oddities in the :doc:`the api instructions <api-instructions>`.
