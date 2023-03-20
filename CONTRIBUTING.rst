Contributing
============

Everyone is invited to contribute to this project.
Feel free to create a `pull request`_ .
If you find errors, omissions, inconsistencies or other things
that need improvement, please create an issue_.

.. _issue: https://github.com/audeering/datasets/issues/new/
.. _pull request: https://github.com/audeering/datasets/compare/


Coding Convention
-----------------

We follow the PEP8_ convention for Python code
and check for correct syntax with flake8_.
Exceptions are defined under the ``[flake8]`` section
in :file:`setup.cfg`.

The checks are executed in the CI using `pre-commit`_.
You can enable those checks locally by executing::

    pip install pre-commit  # consider system wide installation
    pre-commit install
    pre-commit run --all-files

Afterwards flake8_ is executed
every time you create a commit.

You can also install flake8_
and call it directly::

    pip install flake8  # consider system wide installation
    flake8

It can be restricted to specific folders::

    flake8 docs/

.. _PEP8: http://www.python.org/dev/peps/pep-0008/
.. _flake8: https://flake8.pycqa.org/en/latest/index.html
.. _pre-commit: https://pre-commit.com


Building the HTML pages
-----------------------

The resulting HTML pages are generated using Sphinx_.
You can install it and a few other necessary packages with::

    pip install -r docs/requirements.txt

To create the HTML pages, run::

	python -m sphinx docs/ build/html -b html

The generated files will be available
in the directory :file:`build/html/`.

It is also possible to automatically check if all links are still valid::

    python -m sphinx docs/ build/linkcheck -b linkcheck

.. _Sphinx: http://sphinx-doc.org/


Creating a New Release
----------------------

New releases are made using the following steps:

#. Update ``CHANGELOG.rst``
#. Commit those changes as "Release X.Y.Z" to a new branch
   and create a pull request
#. Once merged,
   create an (annotated) tag with ``git tag -a X.Y.Z``
#. Push the tag to Github
