..
   SPDX-License-Identifier: CC-BY-SA 4.0

   Copyright (C) 2024 David Aderbauer & The Emailkasten Contributors
   Licensed under the Creative Commons Attribution-ShareAlike 4.0 International License.

API Instructions
================

If you run a Emailkasten server or have access to one, the easiest way
to get started with the API is via the redoc and swagger interfaces.

These can be found under */api/schema/redoc* and */api/schema/swagger*.

Alternatively you can also get a raw OpenAPI schema from */api/schema*.
You can render it to any API overview using one of the existing webtools or the docker image provided by swagger

.. code-block:: bash

    docker run -p 8080:8080 -e SWAGGER_JSON=/schema.yml -v /path/to/schema.yml:/schema.yml swaggerapi/swagger-ui

In general the URLs of the API endpoints are designed in parallel to
the webapps URLs with a prefix */api/v1/*.

.. note::
    All endpoints for interactions with the data and for authentication via api do not end in a slash.

To get an idea of what the different endpoints do try using the webapp
or reading :doc:`its manual <web-instructions>` first.

In addition to the features of the webapp the API offers vastly extended options for filtering.
It also always you to download hand-picked email, attachment and correspondent files in batches as compact mailbox formats.

.. note::
    If you dont proxy Emailkasten and want to request the API, you will have to ignore the self-signed certificate warnings.
    Using cURL you can do so via the `-k` option.


API Schema
----------

.. toctree::
    :maxdepth: 1

    api-schema

The API version of the django-allauth user management is not documented in this schema.
Please refer to `its own OpenAPI schema <https://django-allauth.readthedocs.io/en/latest/headless/openapi-specification/>`_ for full information.
Replace ``_allauth`` in their URLs with ``api/auth`` to map it to the Emailkasten endpoints.


Authentication
--------------

To authenticate via the API you have 4 options:

- Basic auth: Authenticate directly at every endpoint with your credentials.
    This option is only available if you don't have multi-factor-authentication turned on.

    .. code-block:: bash

        curl -kX 'GET' -u user:password https://emailkasten.mydomain.tld/api/v1/emails/1

- Token authentication: Authenticate via an API token.
    You can get a persistent one from the admin panel.

    .. code-block:: bash

        curl -kX 'GET' -H 'Authorization: Token your_key' https://emailkasten.mydomain.tld/api/v1/emails/1

- Session authentication: Authenticate using a session cookie.
    This always requires that you add a CSRF token to the request.

    .. code-block:: bash

        curl -kX 'GET' -b 'sessionid=your_session_cookie; csrftoken=your_csrf_token' -H 'X-CSRFTOKEN: your_csrf_token' https://emailkasten.mydomain.tld/api/v1/emails/1

- Session Token Authentication: Authenticate using a session token.
    This option is implemented by the API of headless django-allauth and is mostly intended for use by alternative frontends.

    .. code-block:: bash

        curl -kX 'POST' -d '{"username": "myname", "password": "mypwd"}' https://emailkasten.mydomain.tld/api/auth/app/v1/auth/login

    This will return a session token in the meta section of the json response.
    Note that the missing / at the end of the login URL is not a typo.

    .. code-block:: bash

        curl -kX 'GET' -H 'X-Session-Token: your_token' https://emailkasten.mydomain.tld/api/v1/emails/1


For more details see `the django restframework documentation on the matter <https://www.django-rest-framework.org/api-guide/authentication/#sessionauthentication>`_.
