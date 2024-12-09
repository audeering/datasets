# musan

This project holds code
to convert the [musan] corpus of music, speech, and noise
to [audformat]
and publish it with [audb]
to a public Artifactory repository
on https://audeering.jfrog.io.

The databases is published under [CC BY 4.0]
and can be downloaded with the Python library [audb]:

```python
import audb

db = audb.load('musan')
```

[CC BY 4.0]: https://creativecommons.org/licenses/by/4.0/
[musan]: https://www.openslr.org/17/
[audb]: https://github.com/audeering/audb/
[audformat]: https://github.com/audeering/audformat/
