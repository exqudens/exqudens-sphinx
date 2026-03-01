# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
import inspect
import json
from pathlib import Path
from logging import LoggerAdapter
from datetime import datetime

# sphinx
from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.util.logging import getLogger as sphinx_util_logging_get_logger

# mlx.traceability
import mlx.traceability

# local
sys.path.append(Path(__file__).parent.as_posix())
from conf_util import ConfUtil
from warning_util import WarningUtil

logger: LoggerAdapter = sphinx_util_logging_get_logger(__name__)
logger.info("-- bgn")

conf_util_obj: ConfUtil = ConfUtil(logger=logger)
warning_util_obj: WarningUtil = WarningUtil(logger=logger)

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

extensions: list[str] = [
    #'sphinx.ext.autodoc',
    #'sphinx.ext.autosectionlabel',
    'linuxdoc.rstFlatTable',
    'mlx.traceability',
    #'breathe',
    #'rst2pdf.pdfbuilder',
    'docxbuilder'
]
templates_path: list[str] = []
exclude_patterns: list[str] = []

# -- Options for AUTO_SECTION_LABEL output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autosectionlabel.html#configuration

#autosectionlabel_prefix_document: bool = False
#autosectionlabel_maxdepth: None | int = None

# -- Options for TRACEABILITY output -------------------------------------------------
# https://melexis.github.io/sphinx-traceability-extension/configuration.html#configuration

traceability_render_relationship_per_item: bool = False
traceability_render_attributes_per_item = False
traceability_attributes: dict[str, str] = {}
traceability_attribute_to_string: dict[str, str] = {}
traceability_relationships: dict[str, str] = {
    'linked_from': 'linked_to'
}
traceability_relationship_to_string: dict[str, str] = {
    'linked_from': 'Linked from',
    'linked_to': 'Linked to'
}
traceability_notifications: dict[str, str] = {}
traceability_json_export_path: None | str = None

# def traceability_inspect_item(name, collection):
#     conf_util_obj.mlx_traceability_inspect_item(
#         name=name,
#         collection=collection,
#         config={
#             'module_': ['implemented_by']
#         }
#     )

# -- Options for BREATHE -------------------------------------------------
# https://breathe.readthedocs.io/en/latest/quickstart.html

#breathe_projects: dict[str, str] = {}
#breathe_domain_by_extension: dict[str, str] = {}
#breathe_default_project: str = 'main'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme: str = 'alabaster'
html_static_path: list[str] = [
    Path(mlx.traceability.__file__).parent.joinpath('assets').as_posix()
]

# -- Options for DOCX output -------------------------------------------------
# https://docxbuilder.readthedocs.io/en/latest/docxbuilder.html#usage

docx_documents: list[tuple[str, str, dict[str, str], bool]] = []
docx_coverpage: bool = False
docx_pagebreak_before_section: int = 0
docx_style: str = Path(__file__).parent.joinpath('style.docx').as_posix()
#docx_style_names: dict[str, str] = {}

# -- Options for PDF output -------------------------------------------------
# https://rst2pdf.org/static/manual.html#sphinx

#pdf_documents: list[tuple[str, str, str, str]] = []
#pdf_use_toc: bool = True
#pdf_use_coverpage: bool = False
#pdf_break_level: int = 2
#pdf_breakside: str = 'any'

# -- Project setup functions -----------------------------------------------------

def project_config_inited(app: Sphinx, config: Config) -> None:
    try:
        logger.info(f"-- [{inspect.currentframe().f_code.co_name}] bgn")

        logger.info(f"-- [{inspect.currentframe().f_code.co_name}] config.project_builder: '{config.project_builder}'")
        logger.info(f"-- [{inspect.currentframe().f_code.co_name}] config.project_subprojects: {config.project_subprojects}")

        project_dir: str = Path(__file__).parent.parent.parent.parent.as_posix()
        logger.info(f"-- [{inspect.currentframe().f_code.co_name}] project_dir: '{project_dir}'")

        conf: dict[str, object] = json.loads(Path(__file__).parent.joinpath('conf.json').read_bytes().decode())
        logger.info(f"-- [{inspect.currentframe().f_code.co_name}] conf: '{json.dumps(conf, indent=4)}'")

        if 'substitutions' in conf:
            conf_substitutions: None | dict[str, str] | object = conf.get('substitutions', None)
            if conf_substitutions is not None and not isinstance(conf_substitutions, dict):
                raise Exception(f"'conf_substitutions' is not an instance of 'dict'")
            if conf_substitutions:
                config.rst_prolog = ''
                for k, v in conf_substitutions.items():
                    config.rst_prolog += f".. |{k}| replace:: {v}\n\n"

        subprojects: dict[str, object] = {}

        if 'subprojects' in conf:
            conf_subprojects: None | dict[str, object] | object = conf.get('subprojects', None)
            if conf_subprojects is not None and not isinstance(conf_subprojects, dict):
                raise Exception(f"'conf_subprojects' is not an instance of 'dict'")
            if conf_subprojects:
                for k, v in conf_subprojects.items():
                    conf_subproject: dict[str, object] = v
                    docx_config: None | dict[str, object] | object = conf_subproject.pop('docx', None)
                    if docx_config is not None and not isinstance(docx_config, dict):
                        raise Exception(f"'docx_config' is not an instance of 'dict'")
                    subprojects[k] = conf_subproject
                    if docx_config:
                        docx_config_properties: dict[str, object] = docx_config.get('docproperties', dict())
                        docx_config_properties['Created'] = datetime.today().strftime('%Y-%m-%dT%H:%M:%S')
                        subprojects[k]['docx'] = (
                            docx_config['startdocname'],
                            docx_config['targetname'],
                            docx_config_properties,
                            docx_config['toctree_only'],
                        )

        logger.info(f"-- [{inspect.currentframe().f_code.co_name}] subprojects: {json.dumps(subprojects, indent=4)}")

        config_project_builder: str = str(config.project_builder) if config.project_builder else ''
        config_project_subprojects: list[str] = list(config.project_subprojects) if config.project_subprojects else []
        supported_subprojects: set[str] = set(subprojects.keys())
        supported_builders: set[str] = {'xml', 'html', 'docx'}
        include_patterns: list[str] = []
        exclude_patterns: list[str] = []

        if config_project_builder not in supported_builders:
            raise Exception(f"unsupported builder name: '{config_project_builder}' supported: {supported_builders}")

        for i, v in enumerate(config_project_subprojects):

            if not v:
                raise Exception(f"'project_subprojects[{i}]' value is none or empty.")

            config_project_subproject: str = str(v)

            if config_project_subproject not in supported_subprojects:
                raise Exception(f"unsupported 'project_subproject': '{config_project_subproject}' supported: {supported_subprojects}")

            if config_project_builder == 'docx':
                config.docx_documents.append(subprojects[config_project_subproject][config_project_builder])
            elif config_project_builder == 'pdf':
                config.docx_documents.append(subprojects[config_project_subproject][config_project_builder])

            if 'include_patterns' in subprojects[config_project_subproject]:
                for include_pattern in subprojects[config_project_subproject]['include_patterns']:
                    include_patterns.append(include_pattern)

            if 'exclude_patterns' in subprojects[config_project_subproject]:
                for exclude_pattern in subprojects[config_project_subproject]['exclude_patterns']:
                    exclude_patterns.append(exclude_pattern)

        if not include_patterns:
            include_patterns.append('**')

        config.include_patterns = include_patterns
        config.exclude_patterns = exclude_patterns

        logger.info(f"-- [{inspect.currentframe().f_code.co_name}] end")
    except Exception as e:
        logger.error(e, exc_info=True)
        raise e

def project_build_finished(app: Sphinx, exception: None | Exception) -> None:
    try:
        logger.info(f"-- [{inspect.currentframe().f_code.co_name}] bgn")

        if exception:
            raise exception

        warning_util_obj.check_warnings(
            input=conf_util_obj.get_sphinx_warnings(),
            file=conf_util_obj.get_sphinx_warnings_file()
        )

        logger.info(f"-- [{inspect.currentframe().f_code.co_name}] end")
    except Exception as e:
        logger.error(e, exc_info=True)
        raise e

def setup(app: Sphinx):
    try:
        app.add_config_value('project_builder', None, True)
        app.add_config_value('project_subprojects', ['index'], True)

        conf_util_obj.sphinx_setup(
            sphinx_application=app
        )

        app.connect('config-inited', project_config_inited)
        app.connect('build-finished', project_build_finished)
    except Exception as e:
        logger.error(e, exc_info=True)
        raise e

logger.info("-- end")
