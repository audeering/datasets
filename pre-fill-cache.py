# As some datasets contain large archives,
# holding several files
# the audb cache can get very large
# when downloading all media examples.
# To avoid this,
# we pre-download all the media files here,
# but clear the audb cache after each dataset.
import os
import shutil
import tempfile

import audb
import audbcards
import audeer

from repository import repository


def cache_media_path(dataset: audbcards.Dataset) -> str:
    r"""Return path to example media in audbcards cache.

    Args:
        dataset: dataset object

    Returns:
        path to example media file in ``audbcards`` cache

    """
    default_audbcards_cache_root = (
        os.environ.get("AUDBCARDS_CACHE_ROOT") or audbcards.config.CACHE_ROOT
    )
    return audeer.path(
        default_audbcards_cache_root,
        dataset.name,
        dataset.version,
        f"{dataset.name}-{dataset.version}-player-media",
        dataset.example_media,
    )


_, _, free = shutil.disk_usage("/")
print(f"Free disk space: {free // (2**30):d} GiB")

audb.config.REPOSITORIES = [repository]
df = audb.available(only_latest=True)
datasets = list(df.index)
print(f"Number of datasets: {len(datasets)}")
for name in datasets:
    version = df.loc[name, "version"]
    with tempfile.TemporaryDirectory() as audb_cache_root:
        audb.config.CACHE_ROOT = audb_cache_root
        ds = audbcards.Dataset(name, version)
        if ds.example_media is not None and not os.path.exists(cache_media_path(ds)):
            print(f"{name}, v{version}: {ds.example_media}", flush=True)
            dc = audbcards.Datacard(ds, sphinx_src_dir="docs")
            dc.player()
