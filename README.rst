========
datasets
========

Overview_ of public datasets
available with audb_.
Each dataset is 
summarized in a data card.

Use the ``audb.load()``
command to load the audio files
and annotations of a dataset.
The following example
loads version 1.4.1 of emodb_:

.. code-block:: python

    db = audb.load("emodb", version="1.4.1")

See also the `audb quickstart guide`_.


.. _audb: https://github.com/audeering/audb
.. _audb quickstart guide: https://audeering.github.io/audb/quickstart.html
.. _emodb: https://audeering.github.io/datasets/datasets/emodb.html
.. _Overview: https://audeering.github.io/datasets/datasets.html
