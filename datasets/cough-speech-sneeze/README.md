# cough-speech-sneeze

This project holds code
to convert the [cough-speech-sneeze] corpus
containing coughing, sneezing, speech, and silence
to [audformat]
and publish it with [audb]
to a public Artifactory repository
on https://audeering.jfrog.io.

The databases is published under [CC BY 4.0]
and can be downloaded with the Python library [audb]:

```python
import audb

db = audb.load('cough-speech-sneeze')
```

[CC BY 4.0]: https://creativecommons.org/licenses/by/4.0/
[cough-speech-sneeze]: https://doi.org/10.1109/ACII.2017.8273622/
[audb]: https://github.com/audeering/audb/
[audformat]: https://github.com/audeering/audformat/
