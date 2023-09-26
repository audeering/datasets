import audb
import audbcards
import audeer


# Configuration -----------------------------------------------------------
REPOSITORIES = [
    audb.Repository(
        name='data-public',
        host='https://audeering.jfrog.io/artifactory',
        backend='artifactory',
    ),
]


# Functions to create data cards -------------------------------------------
def run():

    # Set internal repositories
    audb.config.REPOSITORIES = REPOSITORIES

    print('Get list of available datasets... ', end='', flush=True)
    df = audb.available(only_latest=True)
    df = df.sort_index()
    print('done')

    # Clear existing data cards
    audeer.rmdir('datasets')
    audeer.mkdir('datasets')

    # Iterate datasets and create data card pages
    names = list(df.index)
    versions = list(df['version'])
    datasets = []
    for (name, version) in zip(names, versions):
        print(f'Parse {name}-{version}... ', end='', flush=True)
        dataset = audbcards.Dataset(name, version)
        dc = audbcards.Datacard(dataset)
        dc.save()
        datasets.append(dataset)
        print('done')

    # Create datasets overview page
    audbcards.core.dataset.create_datasets_page(datasets)
