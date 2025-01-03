import audeer

from repository import repository


# Project -----------------------------------------------------------------
project = "datasets"
author = "Hagen Wierstorf, Johannes Wagner"
version = audeer.git_repo_version()
title = project


# General -----------------------------------------------------------------
master_doc = "index"
source_suffix = ".rst"
exclude_patterns = ["build", "Thumbs.db", ".DS_Store"]
extensions = [
    "audbcards.sphinx",
]
pygments_style = None
linkcheck_ignore = [
    "./datasets/emodb.html",
    "https://doi.org",
    "https://sphinx-doc.org/",
    "https://audeering.jfrog.io/artifactory",
    "http://emodb.bilderbar.info/download/download.zip",
]


# HTML --------------------------------------------------------------------
html_theme = "sphinx_audeering_theme"
html_theme_options = {
    "display_version": True,
    "logo_only": False,
    "footer_links": False,
    "wide_pages": ["datasets"],
}
html_context = {
    "display_github": True,
}
html_title = title

audbcards_datasets = [
    (
        "datasets",  # folder name
        "Datasets",  # datasets overview page header
        repository,
        True,  # don't show audio examples
    ),
]
audbcards_templates = "_templates"
