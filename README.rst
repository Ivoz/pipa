Pipa
====

Pipa is a sparten local PyPI server.

It requires Python 3, and runs over self-signed SSL.

This means pip won't give you any warnings when using it.

NOTE: It does *not* currently fetch from PyPI for other packages.

Usage
-----

0. Find help on any pipa command with `pipa <command> -h`.

1. Initialize

   run ``pipa init`` to create a packages folder, server certificates,
   and configuration file (``pipa.cfg``)

2. Add a user

   use ``pipa user -a <username> <password>`` to add a new user to the confg
   that will be able to upload files to pipa.

3. Run the server

   Run ``pipa serve`` to serve with configuration from your config.

4. Configure pip and distutils

   To install packages from pipa, pip needs to be given pipa's index url,
   and its cert bundle to authenticate with. This (``bundle.pem``) should be
   available to both pip and the server; you can copy it to where you need.
   The index url should be printed when starting the server.
   You can specify these with the flags ``--index-url=...`` and ``--cert=...``;
   or the environment variables ``PIP_INDEX_URL`` and ``PIP_CERT``;
   or in a `configuration file <pip.conf>`_.

   pipa allows uploading packages. To configure this, edit your ``~/.pypirc``
   to look something like this::

    [distutils]
    index-servers =
        pypi
        pipa

    [pypi]
    username: my_pypi.python.org_user
    password: pass

    [pipa]
    repository: https://localhost:5351/upload/
    username: <username>
    password: <password>

   Making use of the values you entered in step 2. See `here <pypirc>`_ for
   more info.

5. Upload packages using ``python setup.py sdist upload -r pipa``, and then
   install them again when needed.


.. _pip.conf: http://www.pip-installer.org/en/latest/user_guide.html#configuration
.. _pypirc: http://docs.python.org/2/distutils/packageindex.html#the-pypirc-file

Informations
------------

Q & A
~~~~~

*Q: Can you add caching from PyPI?*

A: I plan to in the future. Pull requests are very welcome. In the mean time,
also check out `devpi`_ and `pypimirror`_.

*Q: Why another PyPI Developer Cache?*

A: I couldn't see one that served over SSL out of the box, and/or that you could
upload to from setup.py

*Q: Why Python 3 only?*

A: Because it's nicer to code in and I want more Python 3 apps, so I made one.

*Q: Are pull requests welcome?*

A: Indeed they are!

.. _devpi: http://doc.devpi.net
.. _pypimirror: https://pypi.python.org/pypi/pypimirror/

------------------

License: MIT

Code: https://github.com/Ivoz/pipa

Issues: https://github.com/Ivoz/pipa/issues
