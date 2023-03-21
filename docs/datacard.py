import os
import shutil
import typing

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import audb
import audeer
import audformat
import audfactory


# Configuration -----------------------------------------------------------
REPOSITORIES = [
    audb.Repository(
        name='data-public',
        host='https://audeering.jfrog.io/artifactory',
        backend='artifactory',
    ),
]
CACHE = audeer.mkdir('./cache')


# Functions to create data cards -------------------------------------------
class Dataset:

    def __init__(
            self,
            name: str,
            version: str,
            repository: str,
            host: str,
    ):
        self.name = name
        self.version = version
        self.repository = repository
        self.host = host

        self.header = audb.info.header(
            name,
            version=version,
            load_tables=True,  # ensure misc tables are loaded
            cache_root=CACHE,
        )
        self.deps = audb.dependencies(
            name,
            version=version,
            cache_root=CACHE,
            verbose=False,
        )

        self._durations = [
            self.deps.duration(file) for file in self.deps.media
        ]
        # Store RST code that should be injected
        # to the actual data card page
        self._rst = ''

        # Clean up cache
        # by removing all other versions of the same dataset
        # to reduce its storage size in CI runners
        versions = audeer.list_dir_names(
            audeer.path(CACHE, name),
            basenames=True,
        )
        other_versions = [v for v in versions if v != version]
        for other_version in other_versions:
            audeer.rmdir(audeer.path(CACHE, name, other_version))

    @property
    def archives(self) -> str:
        r"""Number of archives of media files in dataset."""
        return str(
            len(
                set([self.deps.archive(file) for file in self.deps.media])
            )
        )

    @property
    def bit_depths(self) -> str:
        r"""Bit depths of media files in dataset."""
        return ', '.join(
            set(
                [
                    str(self.deps.bit_depth(file))
                    for file in self.deps.media
                    if self.deps.bit_depth(file)
                ]
            )
        )

    @property
    def channels(self) -> str:
        r"""Channels of media files in dataset."""
        return ', '.join(
            set(
                [
                    str(self.deps.channels(file))
                    for file in self.deps.media
                    if self.deps.channels(file)
                ]
            )
        )

    @property
    def duration(self) -> str:
        r"""Total duration of media files in dataset."""
        return str(
            pd.to_timedelta(
                sum([d for d in self._durations if d is not None]),
                unit='s',
            )
        )

    @property
    def file_durations(self) -> typing.List:
        r"""Distribution of file durations in dataset."""
        min_ = np.min(self._durations)
        max_ = np.max(self._durations)
        plt.figure(figsize=[.5, .15])
        # Remove all margins besides bottom
        plt.subplot(111)
        plt.subplots_adjust(
            left=0,
            bottom=0.2,
            right=1,
            top=1,
            wspace=0,
            hspace=0,
        )
        # Plot duration distribution
        sns.kdeplot(
            self._durations,
            fill=True,
            cut=0,
            clip=(min_, max_),
            linewidth=0,
            alpha=1,
            color='#d54239',
        )
        # Remove al tiks, labels
        sns.despine(left=True, bottom=True)
        plt.tick_params(
            axis='both',
            which='both',
            bottom=False,
            left=False,
            labelbottom=False,
            labelleft=False,
        )
        plt.xlabel('')
        plt.ylabel('')
        plt.savefig('durations.png', transparent=True)
        plt.close()
        self._rst = '.. |durations| image:: ../durations.png\n'
        return f'{min_:.1f} s |durations| {max_:.1f} s'

    @property
    def example(self) -> str:
        r"""Relative path to example media file in dataset."""
        # Pick a meaningful duration for the example audio file
        min_dur = 0.5
        max_dur = 300  # 5 min
        durations = [self.deps.duration(file) for file in self.deps.media]
        selected_duration = np.median(
            [d for d in durations if d >= min_dur and d <= max_dur]
        )
        # Get index for duration closest to selected duration
        # see https://stackoverflow.com/a/9706105
        # durations.index(selected_duration)
        # is an alternative but fails due to rounding errors
        index = min(
            range(len(durations)),
            key=lambda n: abs(durations[n] - selected_duration),
        )
        # Download of example data might fail
        try:
            media = self.deps.media[index]
            audb.load_media(
                self.name,
                media,
                version=self.version,
                cache_root=CACHE,
                verbose=False,
            )
        except:  # noqa: E722
            media = ''
        return media

    @property
    def files(self) -> str:
        r"""Number of media files in dataset."""
        return str(len(self.deps.media))

    @property
    def formats(self) -> str:
        r"""File formats of media files in dataset."""
        return ', '.join(
            set(
                [
                    self.deps.format(file)
                    for file in self.deps.media
                ]
            )
        )

    @property
    def license_link(self) -> str:
        r"""License of dataset as a link if possible."""
        license = self.header.license or 'Unknown'
        if (
                self.header.license_url is None
                or len(self.header.license_url) == 0
        ):
            return license
        else:
            return f'`{license} <{self.header.license_url}>`__'

    @property
    def name_link(self) -> str:
        r"""Name of dataset as internal link to data card."""
        return f'`{self.name} <./datasets/{self.name}.html>`__'

    @property
    def publication(self) -> str:
        r"""Date and author uploading dataset to repository."""
        url = (
            f'{self.host}/{self.repository}/{self.name}/'
            f'db/{self.version}/db-{self.version}.zip'
        )
        path = audfactory.path(url)
        stat = path.stat()
        return f'{stat.ctime:%Y-%m-%d} by {stat.created_by}'

    @property
    def repository_link(self) -> str:
        r"""Repository name with link to dataset in Artifactory web UI."""
        url = (
            f'{self.host}/'
            f'webapp/#/artifacts/browse/tree/General/'
            f'{self.repository}/'
            f'{self.name}'
        )
        return f'`{self.repository} <{url}>`__'

    @property
    def sampling_rates(self) -> str:
        r"""Sampling rates of media files in dataset."""
        return ', '.join(
            set(
                [
                    str(self.deps.sampling_rate(file))
                    for file in self.deps.media
                    if self.deps.sampling_rate(file)
                ]
            )
        )

    @property
    def schemes(self) -> str:
        r"""List schemes of dataset.

        For the schemes ``'speaker'`` and ``'emotion'``
        it incorporates mappings in brackets,
        e.g. ``'speaker: [age, gender, language]'``.

        """
        return format_schemes(self.header.schemes)

    @property
    def short_description(self) -> str:
        r"""Description of dataset shortened to 150 chars."""
        length = 150
        description = self.header.description or ''
        # Fix RST used signs
        description = description.replace('`', "'")
        if len(description) > length:
            description = f'{description[:length - 3]}...'
        return description

    @property
    def version_link(self) -> str:
        r"""Version of dataset as link to changelog on Github."""
        github = 'https://github.com/audeering'
        branch = 'main'
        url = f'{github}/{self.name}/blob/{branch}/CHANGELOG.md'
        return f'`{self.version} <{url}>`__'


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
    repositories = list(df['repository'])
    hosts = list(df['host'])
    zips = zip(names, versions, repositories, hosts)
    datasets = []
    for (name, version, repository, host) in zips:
        print(f'Parse {name}-{version}... ', end='', flush=True)
        dataset = Dataset(name, version, repository, host)
        create_datacard_page(dataset)
        datasets.append(dataset)
        print('done')

    # Create datasets overview page
    create_datasets_page(datasets)


def create_datacard_page(dataset: Dataset):
    r"""Create a dedicated sub-page for the data card.

    This creates the RST file ``docs/datasets/{dataset}.rst``
    containing the data card for the given dataset.

    If an audio example is provided for the dataset
    it is copied to the build destination
    under ``build/html/datasets/{dataset}``.

    """
    db = dataset.header

    rst_file = f'datasets/{dataset.name}.rst'
    with open(rst_file, 'w') as fp:

        # Link to page
        fp.write(f'.. _{dataset.name}:\n')
        fp.write('\n')

        # Heading
        fp.write(f'{dataset.name}\n')
        fp.write('-' * len(dataset.name))
        fp.write('\n\n')

        # Author
        if db.author is not None:
            fp.write(f'Created by {db.author}\n')
            fp.write('\n\n')

        # Pre-execute some table entries to prefill _rst
        files = (
            f'{dataset.files} files, '
            f'duraton distribution: {dataset.file_durations}'
        )

        # Inject additional code
        fp.write(f'{dataset._rst}\n')

        # Overview table
        fp.write('=============== ======================\n')
        fp.write(f'version         {dataset.version_link}\n')
        fp.write(f'license         {dataset.license_link}\n')
        fp.write(f'source          {db.source}\n')
        fp.write(f'usage           {db.usage}\n')
        if db.languages is not None:
            fp.write(f'languages       {", ".join(db.languages)}\n')
        fp.write(f'format          {dataset.formats}\n')
        fp.write(f'channel         {dataset.channels}\n')
        fp.write(f'sampling rate   {dataset.sampling_rates}\n')
        fp.write(f'bit depth       {dataset.bit_depths}\n')
        fp.write(f'duration        {dataset.duration}\n')
        fp.write(f'files           {files}\n')
        fp.write(f'repository      {dataset.repository_link}\n')
        fp.write(f'published       {dataset.publication}\n')
        fp.write('=============== ======================\n')
        fp.write('\n\n')

        # Description
        if (
                db.description is not None
                and len(db.description) > 0
        ):
            description = db.description.replace('|', r'\|')
            fp.write('Description\n')
            fp.write('^^^^^^^^^^^\n')
            fp.write('\n')
            fp.write(description)
            fp.write('\n\n')

        # Audio example
        file = dataset.example
        if len(file) > 0:
            src_dir = (
                f'{CACHE}/{audb.flavor_path(dataset.name, dataset.version)}'
            )
            dst_dir = f'../build/html/datasets/{dataset.name}'
            audeer.mkdir(os.path.join(dst_dir, os.path.dirname(file)))
            shutil.copy(
                os.path.join(src_dir, file),
                os.path.join(dst_dir, file),
            )
            src_file = os.path.join(dataset.name, file)
            fp.write('Example\n')
            fp.write('^^^^^^^\n')
            fp.write('\n')
            fp.write(f':file:`{file}`\n')
            fp.write('\n')
            fp.write('.. raw:: html\n')
            fp.write('\n')
            fp.write(f'    <p><audio controls src="{src_file}"></audio></p>\n')
            fp.write('\n')

        # Tables
        tables = list(db)
        types = []
        for table_id in tables:
            table = db[table_id]
            if isinstance(table, audformat.MiscTable):
                types.append('misc')
            else:
                types.append(table.type)
        columns = [list(db[table_id].columns) for table_id in tables]
        fp.write('Tables\n')
        fp.write('^^^^^^\n')
        fp.write('\n')
        fp.write('.. csv-table::\n')
        fp.write('   :header: ID,Type,Columns\n')
        fp.write('   :widths: 20, 10, 70\n')
        fp.write('\n')
        for table, type_, column in zip(tables, types, columns):
            fp.write(f'    "{table}", "{type_}", "{", ".join(column)}"\n')
        fp.write('\n\n')

        # Schemes
        if len(db.schemes) > 0:
            has_minimums = any(
                [db.schemes[s].minimum is not None for s in db.schemes]
            )
            has_maximums = any(
                [db.schemes[s].maximum is not None for s in db.schemes]
            )
            has_labels = any(
                [db.schemes[s].labels is not None for s in db.schemes]
            )
            has_mappings = any(
                [
                    isinstance(db.schemes[s].labels, (str, dict))
                    for s in db.schemes
                ]
            )
            header_line = '   :header: ID,Dtype'
            if has_minimums:
                header_line += ',Min'
            if has_maximums:
                header_line += ',Max'
            if has_labels:
                header_line += ',Labels'
            if has_mappings:
                header_line += ',Mappings'
            header_line += '\n'
            fp.write('Schemes\n')
            fp.write('^^^^^^^\n')
            fp.write('\n')
            fp.write('.. csv-table::\n')
            fp.write(header_line)
            fp.write('\n')
            for scheme_id in db.schemes:
                fp.write(f'    "{scheme_id}", ')
                scheme = db.schemes[scheme_id]
                fp.write(f'"{scheme.dtype}"')
                if has_minimums:
                    minimum = scheme.minimum or ''
                    fp.write(f', "{minimum}"')
                if has_maximums:
                    maximum = scheme.maximum or ''
                    fp.write(f', "{maximum}"')
                if has_labels:
                    if scheme.labels is None:
                        labels = []
                    else:
                        labels = sorted(scheme._labels_to_list())
                        labels = [str(label) for label in labels]
                        # Avoid `_` at end of label,
                        # as this has special meaning in RST (link)
                        labels = [
                            label[:-1] + r'\_'
                            if label.endswith('_')
                            else label
                            for label in labels
                        ]
                        labels = limit_presented_samples(
                            labels,
                            15,
                            replacement_text='[...]',
                        )
                    fp.write(f', "{", ".join(labels)}"')
                if has_mappings:
                    if not isinstance(scheme.labels, (str, dict)):
                        mappings = ''
                    else:
                        labels = scheme._labels_to_dict()
                        # Mappings can contain a single mapping
                        # or a deeper nestings.
                        # In the first case we just present ✓,
                        # in the second case the keys of the nested dict.
                        # {'f': 'female', 'm': 'male'}
                        # or
                        # {'s1': {'gender': 'male', 'age': 21}}
                        mappings = list(labels.values())
                        if isinstance(mappings[0], dict):
                            # e.g. {'s1': {'gender': 'male', 'age': 21}}
                            mappings = sorted(list(mappings[0].keys()))
                            mappings = f'{", ".join(mappings)}'
                        else:
                            # e.g. {'f': 'female', 'm': 'male'}
                            mappings = '✓'
                        fp.write(f', "{mappings}"')
                fp.write('\n')


def create_datasets_page(datasets: typing.Sequence):
    r"""Create overview page of datasets."""
    # Create CSV file with overview of datasets
    tuples = [
        (
            dataset.name_link,
            dataset.short_description,
            dataset.license_link,
            dataset.version,
            dataset.schemes,
        )
        for dataset in datasets
    ]
    df = pd.DataFrame.from_records(
        tuples,
        columns=['name', 'description', 'license', 'version', 'schemes'],
        index='name',
    )
    csv_file = 'datasets.csv'
    df.to_csv(csv_file)
    # Create RST file showing CSV file
    # and adding links to all data cards
    rst_file = 'datasets.rst'
    with open(rst_file, 'w') as fp:

        fp.write('.. _datasets:\n')
        fp.write('\n')
        fp.write('Datasets\n')
        fp.write('========\n')
        fp.write('\n')
        fp.write('Datasets available with audb_ as of |today|.\n')
        fp.write('For each dataset, the latest version is shown.\n')
        fp.write('\n')
        fp.write('.. csv-table::\n')
        fp.write('    :header-rows: 1\n')
        fp.write('    :widths: 10, 20, 7, 4, 25\n')
        fp.write(f'    :file: {csv_file}\n')
        fp.write('\n')
        fp.write('.. _audb: https://audeering.github.io/audb/\n')
        fp.write('\n')
        fp.write('\n')
        fp.write('.. toctree::\n')
        fp.write('    :maxdepth: 1\n')
        fp.write('    :hidden:\n')
        fp.write('\n')
        # Add links to data cards
        for dataset in datasets:
            fp.write(f'    datasets/{dataset.name}\n')


def format_schemes(
        schemes,
        excludes=['duration'],
        max_schemes=15,
):
    """Convert schemes object into string.

    It lists the main annotaton schemes
    of the datasets,
    and collects additional information
    on schemes calles `emotion` and `speaker`.

    """
    # Filter schemes
    filtered_schemes = []
    emotion = []
    speaker = []
    for scheme in schemes:
        if scheme in excludes:
            continue
        # schemes[scheme] entries are always dictionaries,
        # so we don't have to check for that
        if scheme == 'emotion':
            try:
                labels = schemes[scheme]._labels_to_list()
                labels = audeer.flatten_list(labels)
                emotion = [{scheme: labels}]
                max_schemes -= 1
            except KeyError:
                emotion = [scheme]
        elif scheme == 'speaker':
            try:
                labels = schemes[scheme]._labels_to_dict()
                labels = list(labels.values())
                # Store the dictionary keys for speaker
                # as those are gender, language, ...
                # Keys are the same for all entries,
                # using the first one is enough
                labels = list(labels[0].keys())
                speaker = [{scheme: labels}]
                max_schemes -= 1
            except KeyError:
                emotion = [scheme]
            except AttributeError:
                emotion = [scheme]
        else:
            filtered_schemes.append(scheme)
    # Force emotion and speaker to the beginning of the list
    filtered_schemes = emotion + speaker + filtered_schemes
    # Limit to maximum number of schemes and add '...' for longer once
    max_schemes = max(max_schemes, 2)
    filtered_schemes = limit_presented_samples(filtered_schemes, max_schemes)
    # Format the information for display
    info_str = ''
    for scheme in filtered_schemes:
        if isinstance(scheme, dict):
            key = list(scheme.keys())[0]
            info_str += f'{key}: ['
            for label in scheme[key]:
                info_str += f'{label}, '
            info_str = info_str[:-2] + '], '
        else:
            info_str += f'{scheme}, '
    info_str = info_str[:-2]

    return info_str


def limit_presented_samples(
        samples: typing.Sequence,
        limit: int,
        replacement_text: str = '...',
) -> typing.List:
    r"""Limit the printing of sequences.

    If the sequence contains too many samples,
    they will be cut out in the center.

    Args:
        samples: sequence of samples to list on screen
        limit: maximum number to present
        replacement_text: text shown instead of removed samples

    Returns:
        string listing the samples

    """
    if len(samples) >= limit:
        samples = (
            samples[:limit // 2]
            + [replacement_text]
            + samples[-limit // 2:]
        )
    return samples
