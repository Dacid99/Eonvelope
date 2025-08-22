API Instructions
================

If you run a Emailkasten server or have access to one, the easiest way
to get started with the API is via the redoc and swagger interfaces.

These can be found under */api/schema/redoc* and */api/schema/swagger*.

Alternatively you can also download a raw OpenAPI schema from */api/schema*.
You can render it to any API overview using one of the existing webtools.

If you have no capability to run the server, you can use the `API schema`_ linked below.

In general the URLs of the API endpoints are designed in parallel to
the webapps URLs with a prefix */api/v1/*.

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


Authentication
--------------

To authenticate via the API you have 3 options:

- Basic auth: Authenticate directly at every endpoint with your credentials

    .. code-block:: bash

        curl -kX 'GET' -u user:password https://emailkasten.mydomain.tld/api/v1/emails/1/

- Token authentication: Authenticate via an API token.
    You can either get a persistent one from the admin panel or a temporary one from the API login via

    .. code-block:: bash

        curl -kX 'POST' -d '{"username": "myname", "password": "mypwd"}' https://emailkasten.mydomain.tld/api/login/

    This will return a key that you can then use in further requests.

    .. code-block:: bash

        curl -kX 'GET' -H 'Authorization: Token your_keys' https://emailkasten.mydomain.tld/api/v1/emails/1/

- Session authentication: Authenticate using a session cookie.
    This always requires that you add a CSRF token to the request.

    .. code-block:: bash

        curl -kX 'GET' -b 'sessionid=your_session_cookie; csrftoken=your_csrf_token' -H 'X-CSRFTOKEN: your_csrf_token' https://emailkasten.mydomain.tld/api/v1/emails/1/

For more details see `the django restframework documentation on the matter <https://www.django-rest-framework.org/api-guide/authentication/#sessionauthentication>`_.
