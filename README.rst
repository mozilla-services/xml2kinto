xml2kinto
---------

Synchronizes an XML file with a Kinto collection.

To run it, make sure you have Python and virtualenv, and run::

    $ make update-blocklist-file
    $ make sync

This will update the Stage instance by default. If you want to
run the script against another Kinto endpoint, you can specify
it using the **KINTO_SERVER** variable.

Example ::

    $ make sync KINTO_SERVER=http://localhost:8888/v1
