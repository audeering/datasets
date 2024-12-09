# micirp

This project holds code
to convert the [micirp] dataset of microphone impulse responses
to [audformat]
and publish it with [audb]
to a public Artifactory repository
on https://audeering.jfrog.io.

The databases is published under [CC BY SA 4.0]
and can be downloaded with the Python library [audb]:

```python
import audb

db = audb.load('micirp')
```

[CC BY SA 4.0]: https://creativecommons.org/licenses/by-sa/4.0/
[micirp]: https://micirp.blogspot.com
[audb]: https://github.com/audeering/audb/
[audformat]: https://github.com/audeering/audformat/
