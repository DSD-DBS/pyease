..
   SPDX-FileCopyrightText: Copyright DB Netz AG and the pyease contributors
   SPDX-License-Identifier: Apache-2.0

pyease
======

.. image:: https://github.com/DSD-DBS/pyease/actions/workflows/build-test-publish.yml/badge.svg

.. image:: https://github.com/DSD-DBS/pyease/actions/workflows/lint.yml/badge.svg

Python Library with helpful functions for the Eclipse Advanced Scripting
Environment (EASE). See https://www.eclipse.org/ease

Documentation
-------------

Read the `full documentation on Github pages`__.

__ https://dsd-dbs.github.io/pyease

Installation
------------

You can install the latest released version directly from PyPI.

.. code::

    pip install pyease

To set up a development environment, clone the project and install it into a
virtual environment.

.. code::

    git clone https://github.com/DSD-DBS/pyease
    cd pyease
    python -m venv .venv

    source .venv/bin/activate.sh  # for Linux / Mac
    .venv\Scripts\activate  # for Windows

    pip install -U pip pre-commit
    pip install -e '.[docs,test]'
    pre-commit install

Contributing
------------

We'd love to see your bug reports and improvement suggestions! Please take a
look at our `guidelines for contributors <CONTRIBUTING.rst>`__ for details.

Licenses
--------

This project is compliant with the `REUSE Specification Version 3.0`__.

__ https://git.fsfe.org/reuse/docs/src/commit/d173a27231a36e1a2a3af07421f5e557ae0fec46/spec.md

Copyright DB Netz AG, licensed under Apache 2.0 (see full text in
`<LICENSES/Apache-2.0.txt>`__)

Dot-files are licensed under CC0-1.0 (see full text in
`<LICENSES/CC0-1.0.txt>`__)
