# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from pathlib import Path
from datetime import datetime
import mlx.traceability
from multiproject.utils import get_project

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

copyright = '2023, exqudens'
author = 'exqudens'
release = '1.0.0'
rst_prolog = ''

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'linuxdoc.rstFlatTable',
    'mlx.traceability',
    'multiproject',
    'docxbuilder',
    'rst2pdf.pdfbuilder'
]

templates_path = []
exclude_patterns = []

# -- Options for TRACEABILITY output -------------------------------------------------
# https://melexis.github.io/sphinx-traceability-extension/configuration.html#configuration

traceability_render_relationship_per_item = True

# -- Options for MULTIPROJECT output -------------------------------------------------
# https://sphinx-multiproject.readthedocs.io/en/latest/configuration.html#configuration

multiproject_projects = {
    'all': {'path': '.', 'use_config_file': False},
    'flat-table': {'path': 'flat-table', 'use_config_file': False},
    'numbered-list': {'path': 'numbered-list', 'use_config_file': False},
    'traceability': {'path': 'traceability', 'use_config_file': False}
}

current_project = get_project(multiproject_projects)

if current_project == 'all':
    project = Path(__file__).parent.parent.joinpath('name-version.txt').open().read().split(':')[0].strip()
    rst_prolog += '.. |project| replace:: ' + project
else:
    project = current_project
    rst_prolog += '.. |project| replace:: ' + project

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
        True
    )
]
docx_pagebreak_before_section = 1

# -- Options for PDF output -------------------------------------------------
# https://rst2pdf.org/static/manual.html#sphinx

pdf_documents = [
    ('index', project, release, author)
]
pdf_break_level = 2
pdf_breakside = 'any'
