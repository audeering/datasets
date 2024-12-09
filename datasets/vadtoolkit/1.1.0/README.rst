Version 1.1.0
=============

`VAD Toolkit`_ provides data for voice activity detection (VAD).

Publish
~~~~~~~

1. Install and activate virtual environment, e.g.:

    .. code-block::

        virtualenv --python="/usr/bin/python3" venv
        source venv/bin/activate

2. Install requirements:

    .. code-block::

        pip install -r requirements.txt

3. Run:

    .. code-block::

        python main.py``  # dry-run, check result under '~/audb-host'

    or

    .. code-block::

        python main.py --publish  # publish to Artifactory

.. _`VAD Toolkit`: https://github.com/jtkim-kaist/VAD
