========
datasets
========

Overview_ of publicly available audb_ datasets.
For each dataset
a standardized documentation is provided
in the form of single data card.

You can easily load all audio files
and annotations associated with a dataset
by a single command.
For example, to load version 1.3.0 of emodb_
run

.. code-block:: python

    db = audb.load('emodb', version='1.3.0')

compare the `audb quickstart guide`_.


.. _audb: https://github.com/audeering/audb
.. _audb quickstart guide: https://audeering.github.io/audb/quickstart.html
.. _emodb: https://github.com/audeering/datasets/emodb.html
.. _Overview: https://github.com/audeering/datasets.html
