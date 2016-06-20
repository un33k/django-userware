Django Userware
====================

**A Django application for handling user management**


[![status-image]][status-link]
[![version-image]][version-link]
[![coverage-image]][coverage-link]

Overview
====================

Simplifies normal user activities, such as login/logout, password reset etc.


How to install
====================

    1. easy_install django-userware
    2. pip install django-userware
    3. git clone http://github.com/un33k/django-userware
        a. cd django-userware
        b. run python setup.py
    4. wget https://github.com/un33k/django-userware/zipball/master
        a. unzip the downloaded file
        b. cd into django-userware-* directory
        c. run python setup.py


How to use
====================
Add `userware` to your INSTALLED_APPS.


Running the tests
====================

To run the tests against the current environment:

    python manage.py test


License
====================

Released under a ([BSD](LICENSE.md)) license.


Version
====================
X.Y.Z Version

    `MAJOR` version -- when you make incompatible API changes,
    `MINOR` version -- when you add functionality in a backwards-compatible manner, and
    `PATCH` version -- when you make backwards-compatible bug fixes.

[status-image]: https://secure.travis-ci.org/un33k/django-userware.png?branch=master
[status-link]: http://travis-ci.org/un33k/django-userware?branch=master

[version-image]: https://img.shields.io/pypi/v/django-userware.svg
[version-link]: https://pypi.python.org/pypi/django-userware

[coverage-image]: https://coveralls.io/repos/un33k/django-userware/badge.svg
[coverage-link]: https://coveralls.io/r/un33k/django-userware

[download-image]: https://img.shields.io/pypi/dm/django-userware.svg
[download-link]: https://pypi.python.org/pypi/django-userware
