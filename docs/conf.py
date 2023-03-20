import audeer

import docs.datacard


# Project -----------------------------------------------------------------
project = 'datasets'
author = 'Hagen Wierstorf, Johannes Wagner'
version = audeer.git_repo_version()
title = project


# General -----------------------------------------------------------------
master_doc = 'index'
source_suffix = '.rst'
exclude_patterns = ['build', 'Thumbs.db', '.DS_Store']
pygments_style = None
linkcheck_ignore = [
    './datasets/emodb.html',
    'https://doi.org',
    'https://github.com/audeering/datasets.html',
    'https://github.com/audeering/datasets/emodb.html',
    'https://sphinx-doc.org/',
    'https://audeering.jfrog.io/artifactory',
    'http://emodb.bilderbar.info/download/download.zip',
]


# HTML --------------------------------------------------------------------
html_theme = 'sphinx_audeering_theme'
html_theme_options = {
    'display_version': True,
    'logo_only': False,
    'footer_links': False,
}
html_context = {
    'display_github': True,
}
html_title = title


# Create data cards for each dataset---------------------------------------
#
# Fetch a list of all available datasets
# and create a data card for each if them
# as part ofg the HTML pages.
#
# For configuration options
# look at the header of datacard.py
docs.datacard.run()
