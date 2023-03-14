import audeer

import docs.datacard


# Project -----------------------------------------------------------------
project = 'datasets'
author = 'Hagen Wierstorf'
version = audeer.git_repo_version()
title = '{} Documentation'.format(project)


# General -----------------------------------------------------------------
master_doc = 'index'
source_suffix = '.rst'
exclude_patterns = ['build', 'Thumbs.db', '.DS_Store']
pygments_style = None
linkcheck_ignore = [
    'https://sphinx-doc.org/',
]


# HTML --------------------------------------------------------------------
html_theme = 'sphinx_audeering_theme'
html_theme_options = {
    'display_version': True,
    'logo_only': False,
    # 'wide_pages': ['datasets'],
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
