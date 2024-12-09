# air

This project holds code
to convert the Aachen Impulse Response ([air]) dataset
to [audformat]
and publish it with [audb]
to a public Artifactory repository
on https://audeering.jfrog.io.

The databases is published under MIT
and can be downloaded with the Python library [audb]:

```python
import audb

db = audb.load('air')
```

[air]: https://www.iks.rwth-aachen.de/en/research/tools-downloads/databases/aachen-impulse-response-database/
[audb]: https://github.com/audeering/audb/
[audformat]: https://github.com/audeering/audformat/
