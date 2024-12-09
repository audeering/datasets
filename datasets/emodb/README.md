# emodb

This project holds code
to convert the [emodb] database of acted emotions
to [audformat]
and published it with [audb]
to a public Artifactory
repository on https://audeering.jfrog.io.

The databases is published under the [CC0-1.0] license
and can be downloaded with the Python library [audb] by:

```python
import audb

db = audb.load('emodb')
```

If you use the database, please cite with

```bibtex
@inproceedings{burkhardt2005emodb,
  title={A database of {German} emotional speech.},
  author={Burkhardt, Felix and Paeschke, Astrid and Rolfes, Miriam and Sendlmeier, Walter F and Weiss, Benjamin},
  booktitle={Proceedings of the Annual Conference of the International Speech Communication Association (INTERSPEECH)},
  address={Lisbon, Portugal},
  publisher={ISCA},
  volume={5},
  pages={1517--1520},
  year={2005}
}
```

[CC0-1.0]: https://creativecommons.org/publicdomain/zero/1.0/
[emodb]: http://emodb.bilderbar.info/index-1280.html
[audb]: https://github.com/audeering/audb
[audformat]: https://github.com/audeering/audformat
