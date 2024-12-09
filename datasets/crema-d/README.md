# crema-d

This project holds code
to convert the [crema-d] corpus
to [audformat]
and publish it with [audb]
to a public Artifactory repository
on https://audeering.jfrog.io.

The databases is published under [ODbL 1.0]
and can be downloaded with the Python library [audb]:

```python
import audb

db = audb.load('crema-d')
```

[ODbL 1.0]: http://opendatacommons.org/licenses/odbl/1.0/
[crema-d]: https://github.com/CheyneyComputerScience/CREMA-D/
[audb]: https://github.com/audeering/audb/
[audformat]: https://github.com/audeering/audformat/
