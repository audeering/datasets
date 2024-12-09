import os
import shutil

import audb
import audeer
import audformat


name = 'emodb'
previous_version = '1.3.0'
build_dir = './build'
build_dir = audeer.mkdir(build_dir)

db = audb.load_to(
    build_dir,
    name,
    version=previous_version,
    num_workers=8,
    only_metadata=True,
    cache_root=None,
    verbose=True,
)

# Add BibTeX file as attchment
rel_path = 'docs/burkhardt2005emodb.bib'
abs_path = audeer.path(build_dir, rel_path)
audeer.mkdir(os.path.dirname(abs_path))
shutil.copyfile(rel_path, abs_path)
db.attachments['bibtex'] = audformat.Attachment(
    rel_path,
    description='Bibtex citation entry for INTERSPEECH conference paper.',
)

db.save(build_dir)
