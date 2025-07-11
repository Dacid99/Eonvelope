Integrations
============

You can intertwine this application with other self-hosted services.
The following list contains instructions on how to go about this for the integrations we are
aware of.
If we are missing something, feel free to contribute an extension of this page.

Searxng
-------

The `Searxng <https://docs.searxng.org/>`_ meta search engine can query data from the Emailkasten database.

To get this to work you need to configure a ``json_engine``
in the engines section of ``settings.yml``.
The API endpoint for the email search is:

.. code-block:: text

    /api/v1/emails/?search=

The results are listed under ``'results'``.

You can also integrate searches for all other data that Emailkasten holds.
For instance, to search the attachments data, use:

.. code-block:: text

    /api/v1/attachments/?search=

Similar patterns apply for correspondents, accounts, mailboxes, etc.
Check the API schema or the browsable API for more details.

To grant access, you can create an ``accesstoken`` in the admin panel
or via the browsable API and provide it in the configuration of the ``JSONEngine``.

Here is an exemplary configuration:

.. code-block:: yaml

    - name: emailkasten-emails
      engine: json_engine
      shortcut: em
      categories: [external memory]
      disabled: false
      paging: true
      content_html_to_text: true
      search_url: https://emailkasten.mydomain.tld/api/v1/emails/?search={query}&page={pageno}
      url_query: id
      url_prefix: https://emailkasten.mydomain.tld/api/v1/emails/
      results_query: results
      title_query: email_subject
      content_query: html_bodytext/plain_bodytext
      headers:
        Authorization: your_accesstoken
      about:
        website: https://emailkasten.mydomain.tld/
        use_official_api: true
        require_api_key: true
        results: JSON

See the `Searxng docs on this subject <https://docs.searxng.org/dev/engines/json_engine.html>`_ for more details.
