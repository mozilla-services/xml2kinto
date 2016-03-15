PYTHON_VERSION = python2.7
VIRTUALENV = virtualenv
VENV := $(shell echo $${VIRTUAL_ENV-.venv-$(PYTHON_VERSION)})
PYTHON = $(VENV)/bin/python
DEV_STAMP = $(VENV)/.dev_env_installed.stamp
INSTALL_STAMP = $(VENV)/.install.stamp
TEMPDIR := $(shell mktemp -d)
KINTO_SERVER = https://kinto.stage.mozaws.net/v1


BLOCKLIST_FILE_URL = "https://blocklist.addons.mozilla.org/blocklist/0/default/default/default/default/default/default/default/default/default/default/default/default/default/"
AMO_BLOCKLIST_UI_SCHEMA = "https://raw.githubusercontent.com/mozilla-services/amo-blocklist-ui/master/amo-blocklist.json"

.IGNORE: clean distclean maintainer-clean
.PHONY: all install install-dev virtualenv tests

all: install
install: $(INSTALL_STAMP)
$(INSTALL_STAMP): $(PYTHON) setup.py
	$(VENV)/bin/pip install -Ue .
	touch $(INSTALL_STAMP)

install-dev: $(INSTALL_STAMP) $(DEV_STAMP)
$(DEV_STAMP): $(PYTHON) dev-requirements.txt
	$(VENV)/bin/pip install -r dev-requirements.txt
	touch $(DEV_STAMP)

virtualenv: $(PYTHON)
$(PYTHON):
	$(VIRTUALENV) --python /usr/bin/$(PYTHON_VERSION) $(VENV)
	$(VENV)/bin/pip install -U pip

build-requirements:
	$(VIRTUALENV) $(TEMPDIR)
	$(TEMPDIR)/bin/pip install -Ue .
	$(TEMPDIR)/bin/pip freeze > requirements.txt

tests-once: install-dev
	$(VENV)/bin/py.test --cov-report term-missing --cov-fail-under 100 --cov xml2kinto xml2kinto

tests:
	@rm -fr .coverage
	$(VENV)/bin/tox

functional: need-kinto-running
	$(VENV)/bin/xml2kinto -s http://localhost:8888/v1 -x blocklists.xml -S schemas.json

clean:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -type d | xargs rm -fr

distclean: clean
	rm -fr *.egg *.egg-info/ dist/ build/

maintainer-clean: distclean
	rm -fr .venv* .tox/

sync: install
	$(VENV)/bin/xml2kinto -s $(KINTO_SERVER)

update-blocklist-file:
	wget -O blocklist.xml $(BLOCKLIST_FILE_URL)

update-schemas:
	wget -O schemas.json $(AMO_BLOCKLIST_UI_SCHEMA)

install-kinto: $(VENV)/bin/kinto
$(VENV)/bin/kinto: install
	$(VENV)/bin/pip install kinto

run-kinto: $(VENV)/bin/kinto
	$(VENV)/bin/kinto --ini config/kinto.ini start

need-kinto-running:
	@curl http://localhost:8888/v1 2>/dev/null 1>&2 || (echo "Run 'make run-signer' before starting tests." && exit 1)
