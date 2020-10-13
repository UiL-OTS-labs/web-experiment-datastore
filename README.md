# Web experiment datastore

This Django project provides a generic datastore, intended to store data from
web experiments. 

# Requirements
- Python 3.6+
- Pip (see requirements.txt)
- A WSGI capable web server (not needed for development)
- A SQL database (tested with SQLite and MariaDB)
- When using mariadb: client and dev libraries

# Translations

Against Django standard practice we use _translation keys_ to provide 
translations, instead of wrapping text in one language in gettext calls. While 
this adds the need for translation files for every supported language, it fastly
reduces whitespace weirdness and other issues with the standard approach. 

Keys are formatted in a standard way:

``{django_app}:{location}:{item}(:{optional_extra})*``

- django_app: The django app this key is part of
- location: the location this key presides in, for example:
    - model: it's a model field description
    - form: it's part of a form
    - {template}: it's part of a template called {template}
- item: Identifier for this exact string, for example:
    - header: it's the view's header
    - {field}: the name of the model field
- optional_extra: 0-n extra keys to differentiate different strings for the same
  item. For example, a model field sometimes has a help_text in addition to a
  verbose_name. In that case, the optional_extra should be ``:help_text``

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