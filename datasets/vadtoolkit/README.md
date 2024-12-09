# vadtoolit

This project holds code
to convert the [vadtoolkit] corpus
to [audformat]
and publish it with [audb]
to a public Artifactory repository
on https://audeering.jfrog.io.

The databases can be downloaded with the Python library [audb]:

```python
import audb

db = audb.load('vadtoolkit')
```

[vadtoolkit]: https://github.com/jtkim-kaist/VAD/
[audb]: https://github.com/audeering/audb/
[audformat]: https://github.com/audeering/audformat/
