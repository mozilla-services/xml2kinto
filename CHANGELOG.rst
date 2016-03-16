CHANGELOG
#########

This document describes changes between each past release.

0.1.0 (unreleased)
==================

**Initial version**

- Create collection with the definition of the JSON schema.
- Scrap blocking details on AMO for add-ons and plugins.
- Handle complex XML records reading for Certificate/GFX
  drivers/Add-ons/Plugins.
- Handle import configuration on the CLI.
  - Bucket / Collection names
  - XML and Schema files path
  - Scrapping or not scrapping
  - Schema or not schema
  - Verbosity level
  - Server selection
  - Auth credentials
  - Importation type selection
- Support for kinto-signer triggering
- Full SSL support for Python 2.7
- Full Python 2.7 and Python 3.4/3.5 support
- Parallel scrapping using Gevent
- Handle the enabled flag to activate records
- Makefile rule to update the blocklist
- Makefile rule to update the schema definition
