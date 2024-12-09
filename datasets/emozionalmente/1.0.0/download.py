import audeer


file = audeer.download_url(
    (
        'https://zenodo.org/record/6569824/files/'
        'emozionalmente_dataset.zip?download=1'
    ),
    'emozionalmente_dataset.zip',
    verbose=True,
)
audeer.extract_archive(
    file,
    '.',
    verbose=True,
)
