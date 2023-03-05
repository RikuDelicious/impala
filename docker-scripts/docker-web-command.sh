#!/bin/bash
echo "@start docker-web-command.sh"
echo "### python manage.py migrate --settings impala.settings_devcontainer"
python ./django-project/manage.py migrate --settings impala.settings.devcontainer
echo "### python manage.py flush --noinput --settings impala.settings_devcontainer"
python ./django-project/manage.py flush --noinput --settings impala.settings.devcontainer
echo "### python manage.py createsuperuser --noinput --settings impala.settings_devcontainer"
python ./django-project/manage.py createsuperuser --noinput --settings impala.settings.devcontainer
echo "@end docker-web-command.sh"

/bin/bash -c "while sleep 1000; do :; done"