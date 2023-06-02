# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
import os
import mlx.traceability
from pathlib import Path
from datetime import datetime

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = Path(__file__).parent.joinpath('name-version.txt').open().read().split(':')[0].strip()
copyright = '2023, exqudens'
author = 'exqudens'
release = Path(__file__).parent.joinpath('name-version.txt').open().read().split(':')[1].strip()
rst_prolog = '.. |project| replace:: ' + project

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

sys.path.append(os.path.normpath(Path(__file__).parent.parent.parent.parent.joinpath('src', 'test', 'py')))

extensions = [
    'sphinx.ext.autodoc',
    'linuxdoc.rstFlatTable',
    'mlx.traceability',
    'docxbuilder',
    'rst2pdf.pdfbuilder'
]

templates_path = []
exclude_patterns = []

# -- Options for TRACEABILITY output -------------------------------------------------
# https://melexis.github.io/sphinx-traceability-extension/configuration.html#configuration

traceability_render_relationship_per_item = True
traceability_notifications = {
    'undefined-reference': 'UNDEFINED_REFERENCE'
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = [str(Path(mlx.traceability.__file__).parent.joinpath('assets'))]

# -- Options for DOCX output -------------------------------------------------
# https://docxbuilder.readthedocs.io/en/latest/docxbuilder.html#usage

docx_documents = [
    (
        'index',
        project + '.docx',
        {
            'title': project + ' documentation',
            'created': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            'subject': project + '-' + release,
            'keywords': ['sphinx']
        },
        False
    )
]
docx_coverpage = False
#docx_pagebreak_before_section = 1

# -- Options for PDF output -------------------------------------------------
# https://rst2pdf.org/static/manual.html#sphinx

pdf_documents = [
    ('index', project, release, author)
]
pdf_use_toc = True
pdf_use_coverpage = False
#pdf_break_level = 2
#pdf_breakside = 'any'
