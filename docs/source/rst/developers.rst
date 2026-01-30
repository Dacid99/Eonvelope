..
   SPDX-License-Identifier: CC-BY-SA 4.0

   Copyright (C) 2024 David Aderbauer & The Eonvelope Contributors
   Licensed under the Creative Commons Attribution-ShareAlike 4.0 International License.

Developers Section
==================

We welcome everyone who wants to contribute to this project!

To get you started quickly and without unnecessary hickups,
please make sure to read the guidelines for developers.

.. toctree::
    :maxdepth: 1

    development
    contributing
    code_of_conduct


The full source code documentation can be found here

.. toctree::
    :maxdepth: 1

    modules


Graphical representation of the project code are shown on these pages

.. toctree::
    :maxdepth: 1

    db-graph
    import-graph


Where To Start
--------------

If you are looking for a thing to help with please check out the ToDo list for ideas

.. toctree::
    :maxdepth: 1

    todo

Migrations
^^^^^^^^^^

Maybe you are using Eonvelope in parallel to another similar service.
Programs that migrate databases from other applications to the Eonvelope database layout are always welcome.

If you are interested in such an endeavour, please get in touch.


You can find an interactive graphical representation of the Eonvelope database layout
under the */db-schema/* url of your instance
or :doc:`on this page <db-graph>`.
We are always happy to help and give additional detailed information about the database layout.


Frontend Development
^^^^^^^^^^^^^^^^^^^^

If you are interested in implementing a frontend option for Eonvelope, you are invited to do so.

Especially mobile development is very welcome!

To allow other frontends to use the same logic and user management as the native web frontend,
the allauth views have an analogous API that can be used in its place.

All other data can be accessed via the api endpoints designed in parallel to the web frontend pages.

See the :doc:`API Instructions <api-instructions>` for more details.

If you feel like there's anything missing, please give us a heads up about it!
