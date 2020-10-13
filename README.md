# Web experiment datastore

This Django project provides a generic datastore, intended to store data from
web experiments. 

# Requirements
- Python 3.6+
- Pip (see requirements.txt)
- A WSGI capable web server (not needed for development)
- A SQL database (tested with SQLite and MariaDB)
- When using mariadb: client and dev libraries

# Installation

For production/acceptation deployment, please see our Puppet module. 
(Hosted on our private GitLab server).

Development instructions:
* Clone this repository
* Install the dependencies using pip (it is recommended to use a virtual 
  environment!). ``pip install -r requirements.txt``
* Run all DB migrations ``python manage.py migrate``
* Run all auditlog migrations ``python manage.py migrate --database auditlog``
* Edit ``ppn_backend/settings.py`` to suit your needs.
* Create a super user using ``python manage.py createsuperuser``
* Compile the translation files using ``python manage.py compilemessages``
* You can now run a development server with ``python manage.py runserver``


## A note on dependencies
We use pip-tools to manage our dependencies (mostly to freeze the versions 
used). It's listed as a dependency, so it will be installed automatically.

``requirements.in`` lists the actual dependency and their version constraints. 
To update ``requirements.txt``, edit ``requirements.in`` and run 
``pip-compile -U``. Don't forget to test with the new versions!