xml2kinto
---------

Synchronizes an XML file with a Kinto collection.

To run it, make sure you have Python 2.7 and virtualenv, and run::

    $ make sync

This will update the Stage instance by default. If you want to
run the script against another Kinto endpoint, you can specify
it using the **KINTO_SERVER** variable.

You can also use **update-blocklist-file** to update the local
blocklist.xml file prior to syncing Kinto.

Example of a full update ::

    $ git clone git@github.com:mozilla-services/xml2kinto.git xml2kinto
    $ cd xml2kinto
    $ git checkout onecrl-stable
    $ make update-blocklist-file
    $ make sync KINTO_SERVER=http://localhost:8888/v1

