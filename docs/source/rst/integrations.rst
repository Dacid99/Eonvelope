..
   SPDX-License-Identifier: CC-BY-SA 4.0

   Copyright (C) 2024 David Aderbauer & The Eonvelope Contributors
   Licensed under the Creative Commons Attribution-ShareAlike 4.0 International License.

Integrations
============

You can intertwine this application with other self-hosted services.
The following list contains instructions on how to go about this for the integrations we are
aware of.
If there's something here,
feel free to contribute an extension of this page or please give us a heads-up about it.


Paperless-ngx
-------------

Eonvelope can send selected attachment files to Paperless for further archival.

You can set the URL and API key for your Paperless server in your profile settings.
The persistent API key can be found in the Paperless webinterface under *My Profile - API Authentication Token*

Optionally, you can set whether that instance has Tika enabled and is thus able to process additional document filetypes.

You can then trigger the action via the button in the webpage showing a single attachment or the related API endpoint.


Immich
------

Eonvelope can send selected attachment files like images and videos to Immich.

You can set the URL and API key for your Immich server in your profile settings.
The persistent API key can be created in the Immich admin webinterface.

You can then trigger the action via the button in the webpage showing a single attachment or the related API endpoint.


Nextcloud
---------

Eonvelope can put selected correspondent data into your Nextcloud addressbook.

You can set the URL of your Nextcloud server as well as your username and password/app-password in your profile settings.

You can then trigger the action via the button in the webpage showing a single correspondent or the related API endpoint.


Searxng
-------

The `Searxng <https://docs.searxng.org/>`_ meta search engine can query data from the Eonvelope database.

To get this to work you need to configure a ``json_engine``
in the engines section of ``settings.yml``.
The API endpoint for the email search is:

.. code-block:: text

    /api/v1/emails?search=

The search results are listed under ``'results'``.

You can also integrate searches for all other data that Eonvelope holds.
For instance, to search the attachments data, use:

.. code-block:: text

    /api/v1/attachments?search=

Similar patterns apply for correspondents, accounts, mailboxes, etc.
Check the API schema or the browsable API for more details.

To grant access, you can create a persistent ``accesstoken`` in the admin panel
and provide it in the configuration of the ``JSONEngine``.

Here is an exemplary configuration:

.. code-block:: yaml

    - name: eonvelope-emails
      engine: json_engine
      shortcut: emls
      categories: [ external memory ]
      disabled: false
      paging: true
      content_html_to_text: true
      search_url: https://<eonvelope.mydomain.tld>/api/v1/emails?search={query}&page={pageno}
      verify: false
      url_query: id
      url_prefix: https://<eonvelope.mydomain.tld>/emails/
      results_query: results
      title_query: email_subject
      content_query: plain_bodytext
      headers:
        Authorization: token <your_accesstoken>
      about:
        website: https://<eonvelope.mydomain.tld>/
        official_api_documentation: https://<eonvelope.mydomain.tld>/api/schema/swagger/
        use_official_api: true
        require_api_key: true
        results: JSON

Adapt this for your setup by exchanging all variables in <> brackets.
In case you prefer the redoc over the swagger api docs, you can switch that too.
If the connection to the eonvelope instance is not using its self-signed certificate (e.g. because you reverse-proxy),
you can ditch the 'verify: false' line.

To search something other than emails,
exchange 'emails' with the data name your interested in, e.g. 'attachments'.
Then pick content_query parameters based on what info you'd like to be shown in the searxng interface.
Dont forget to come up with a different shortcut name.

See the `Searxng docs on this subject <https://docs.searxng.org/dev/engines/json_engine.html>`_ for more details.


Prometheus
----------

Eonvelope exports database, database-models, migrations, cache and other metrics for Prometheus.
The metrics data can be scraped under `/metrics`, their names all start with ``eonvelope``.

For reference on configuration refer to the [Prometheus](https://prometheus.io/docs/introduction/overview/) and [django-prometheus](https://github.com/django-commons/django-prometheus/blob/master/README.md) docs.
