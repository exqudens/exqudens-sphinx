import sys
import inspect
from logging import LoggerAdapter
from logging import LogRecord
from logging import getLogger as logging_get_logger
from typing import Deque
from pathlib import Path

# docutils
import docutils.nodes
from docutils.nodes import Node as DocUtilsNode
from docutils.nodes import Text as DocUtilsText
from docutils.nodes import NodeVisitor as DocUtilsNodeVisitor
from docutils.nodes import TreePruningException as DocUtilsTreePruningException

# sphinx
from sphinx.application import Sphinx
from sphinx.util.logging import WarningSuppressor
from sphinx.util import Tee

# mlx.traceability
from mlx.traceability import TraceableCollection as MlxTraceableCollection
from mlx.traceable_item import TraceableItem as MlxTraceableItem
from mlx.traceability_exception import TraceabilityException as MlxTraceabilityException

# docxbuilder
from docxbuilder import DocxBuilder
from docxbuilder.writer import DocxTranslator

class ConfUtil:
    """
    ConfUtil class.
    """
    __logger: None | LoggerAdapter = None

    __sphinx_warnings_file: None | str = None
    __sphinx_warnings: None | Deque[LogRecord] = None
    __sphinx_old_util_logging_warning_suppressor_filter = None
    __sphinx_new_util_logging_warning_suppressor_filter = None

    __docutils_text_visited_nodes: None | Deque[DocUtilsNode] = None
    __docutils_old_dispatch_visit = None
    __docutils_new_dispatch_visit = None
    __docutils_old_dispatch_departure = None
    __docutils_new_dispatch_departure = None

    __docxbuilder_assemble_doctree_log: bool = False
    __docxbuilder_assemble_doctree_log_before: bool = False
    __docxbuilder_assemble_doctree_log_after: bool = False
    __docxbuilder_old_assemble_doctree = None
    __docxbuilder_new_assemble_doctree = None

    def __init__(
        self,
        logger: None | LoggerAdapter | object
    ) -> None:
        try:
            if logger is not None and isinstance(logger, LoggerAdapter):
                self.__logger = logger
            else:
                self.__logger = logging_get_logger('.'.join([__class__.__module__, __class__.__name__]))
        except Exception as e:
            if self.__logger: self.__logger.error(e, exc_info=True)
            raise e

    def sphinx_setup(
        self,

        sphinx_application: None | Sphinx | object,
        sphinx_warnings_size: int = 0,
        sphinx_util_logging_warning_suppressor_filter_override: bool = True,

        docutils_text_visited_nodes_size: int = 0,
        docutils_dispatch_visit_override: bool = True,
        docutils_dispatch_departure_override: bool = True,

        docxbuilder_assemble_doctree_log: bool = False,
        docxbuilder_assemble_doctree_log_before: bool = False,
        docxbuilder_assemble_doctree_log_after: bool = False,
        docxbuilder_assemble_doctree_override: bool = True
    ) -> None:
        try:
            if sphinx_application is None:
                raise Exception("'sphinx_application' is none!")
            elif not isinstance(sphinx_application, Sphinx):
                raise Exception(f"'sphinx_application' is not an instance of 'Sphinx' it is instance of '{type(sphinx_application)}'")

            if sphinx_application._warning is not None and isinstance(sphinx_application._warning, Tee):
                self.__sphinx_warnings_file = sphinx_application._warning.stream2.name

            if sphinx_util_logging_warning_suppressor_filter_override:
                self.__sphinx_warnings = Deque([], sphinx_warnings_size) if sphinx_warnings_size > 0 else Deque([])
                self.__sphinx_old_util_logging_warning_suppressor_filter = getattr(WarningSuppressor, 'filter')
                self.__sphinx_new_util_logging_warning_suppressor_filter = lambda sphinx_self, record: self.sphinx_util_logging_warning_suppressor_filter(sphinx_self, record)
                setattr(WarningSuppressor, 'filter', self.__sphinx_new_util_logging_warning_suppressor_filter)

            if docutils_dispatch_visit_override or docutils_dispatch_departure_override:
                self.__docutils_text_visited_nodes = Deque([], docutils_text_visited_nodes_size) if docutils_text_visited_nodes_size > 0 else Deque([])
            if docutils_dispatch_visit_override:
                self.__docutils_old_dispatch_visit = getattr(DocUtilsNodeVisitor, 'dispatch_visit')
                self.__docutils_new_dispatch_visit = lambda docutils_self, node: self.docutils_dispatch_visit(docutils_self, node)
                setattr(DocUtilsNodeVisitor, 'dispatch_visit', self.__docutils_new_dispatch_visit)
            if docutils_dispatch_departure_override:
                self.__docutils_old_dispatch_departure = getattr(DocUtilsNodeVisitor, 'dispatch_departure')
                self.__docutils_new_dispatch_departure = lambda docutils_self, node: self.docutils_dispatch_departure(docutils_self, node)
                setattr(DocUtilsNodeVisitor, 'dispatch_departure', self.__docutils_new_dispatch_departure)

            self.__docxbuilder_assemble_doctree_log = docxbuilder_assemble_doctree_log
            self.__docxbuilder_assemble_doctree_log_before = docxbuilder_assemble_doctree_log_before
            self.__docxbuilder_assemble_doctree_log_after = docxbuilder_assemble_doctree_log_after

            if docxbuilder_assemble_doctree_override:
                self.__docxbuilder_old_assemble_doctree = getattr(DocxBuilder, 'assemble_doctree')
                self.__docxbuilder_new_assemble_doctree = lambda docxbuilder_self, master, toctree_only: self.docxbuilder_assemble_doctree(docxbuilder_self, master, toctree_only)
                setattr(DocxBuilder, 'assemble_doctree', self.__docxbuilder_new_assemble_doctree)
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e

    def get_sphinx_warnings_file(self) -> None | str:
        try:
            return self.__sphinx_warnings_file
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e

    def get_sphinx_warnings(self) -> list[dict[str, str]]:
        try:
            result: list[dict[str, str]] = []
            for v in self.__sphinx_warnings:
                record: LogRecord = v
                record_location: str = getattr(record, 'location', '')
                record_levelname: str = record.levelname
                record_message: str = ''
                if record_location:
                    record_location = Path(record_location).as_posix()
                try:
                    record_message = record.msg % record.args
                except (TypeError, ValueError):
                    record_message = record.msg  # use record.msg itself
                entry: dict[str, str] = {
                    'location': record_location,
                    'levelname': record_levelname,
                    'message': record_message
                }
                result.append(entry)
            return result
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e

    def log_message_as_warning_or_error(
        self,
        message: None | str | object,
        as_error: bool = True,
        exit_code: int = 1
    ) -> None:
        try:
            if as_error:
                self.__logger.error(message)
                sys.exit(exit_code)
            else:
                self.__logger.warning(message)
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e

    def sphinx_util_logging_warning_suppressor_filter(
        self,
        sphinx_self,
        record: LogRecord
    ) -> bool:
        try:
            self.__sphinx_warnings.append(record)
            return self.__sphinx_old_util_logging_warning_suppressor_filter(sphinx_self, record)
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e

    def docutils_to_string(
        self,
        node: None | DocUtilsNode,
        include_path: bool = True
    ) -> str:
        try:
            if node is None:
                raise Exception("'node' is None")
            if include_path:
                path = []
                n = node
                while n is not None:
                    path.append(n)
                    n = n.parent
                path.reverse()
                path.pop(len(path) - 1)
                strings = [i.astext() if isinstance(i, DocUtilsText) else i.__class__.__name__ for i in path]
                node_string = "['" + "', '".join(strings) + "']: '" + (node.astext() if isinstance(node, DocUtilsText) else node.__class__.__name__)
            else:
                node_string = node.astext() if isinstance(node, DocUtilsText) else node.__class__.__name__
            return node_string
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e

    def docutils_log_node(
        self,
        node: DocUtilsNode
    ) -> None:
        try:
            self.__logger.info(f"-- {inspect.currentframe().f_code.co_name} start")
            nodes = node.traverse()
            entries = []
            for node in nodes:
                if isinstance(node, DocUtilsText) or len(node) == 0:
                    entry = []
                    n = node
                    while n is not None:
                        entry.append(n)
                        n = n.parent
                    entry.reverse()
                    strings = [i.astext() if isinstance(i, DocUtilsText) else i.__class__.__name__ for i in entry]
                    entries.append(strings)
            for entry in entries:
                self.__logger.info(f"-- {entry}")
            self.__logger.info(f"-- {inspect.currentframe().f_code.co_name} end")
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e

    def docutils_find_nodes(
        self,
        node: DocUtilsNode,
        class_names: None | list[str] = None,
        index_key: None | str = None,
        include_self: bool = False
    ) -> list[DocUtilsNode]:
        try:
            if class_names is None:
                raise Exception("Unspecified 'class_names'")

            if index_key is None:
                raise Exception("Unspecified 'index_key'")

            result: list[DocUtilsNode] = []

            for n in node.traverse(include_self=include_self):
                if n.__class__.__name__ in class_names:
                    n[index_key] = len(result)
                    result.append(n)

            return result
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e

    def docutils_dispatch_visit(
        self,
        docutils_self,
        node: DocUtilsNode
    ):
        try:
            if node is not None and node.__class__.__name__ == 'Text':
                self.__docutils_text_visited_nodes.append(node)
            return self.__docutils_old_dispatch_visit(docutils_self, node)
        except DocUtilsTreePruningException as e:
            raise e
        except Exception as e:
            for n in self.__docutils_text_visited_nodes:
                self.__logger.error(f"-- {inspect.currentframe().f_code.co_name} (previous): {self.docutils_to_string(n)}")
            self.__logger.error(f"-- {inspect.currentframe().f_code.co_name} (current): {self.docutils_to_string(node)}")
            self.__logger.error(e, exc_info = True)
            raise e

    def docutils_dispatch_departure(
        self,
        docutils_self,
        node: DocUtilsNode
    ):
        try:
            return self.__docutils_old_dispatch_departure(docutils_self, node)
        except DocUtilsTreePruningException as e:
            raise e
        except Exception as e:
            for n in self.__docutils_text_visited_nodes:
                self.__logger.error(f"-- {inspect.currentframe().f_code.co_name} (previous): '{self.docutils_to_string(n)}'")
            self.__logger.error(f"-- {inspect.currentframe().f_code.co_name} (current): {self.docutils_to_string(node)}")
            self.__logger.error(e, exc_info = True)
            raise e

    def docxbuilder_unwrap(
        self,
        value: DocUtilsNode,
        class_names: None | list[str] = None
    ) -> DocUtilsNode:
        try:
            if class_names is None:
                raise Exception("Unspecified 'class_names'")

            value_nodes = []

            for node in value:
                value_nodes.append(node)

            result: DocUtilsNode = value
            result.clear()

            for node in value_nodes:
                if node.__class__.__name__ == 'paragraph':
                    paragraph = docutils.nodes.paragraph()
                    for n in node:
                        if n.__class__.__name__ in class_names:
                            if len(paragraph) > 0:
                                result.append(paragraph)
                                paragraph = docutils.nodes.paragraph()
                            result.append(n)
                        else:
                            paragraph.append(n)
                    if len(paragraph) > 0:
                        result.append(paragraph)
                else:
                    result.append(node)

            return result
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e

    def docxbuilder_fix_node(
        self,
        value: DocUtilsNode
    ) -> DocUtilsNode:
        try:
            if value.__class__.__name__ == 'table':
                for table_node in value:
                    if table_node.__class__.__name__ == 'tgroup':
                        for tgroup_node in table_node:
                            if tgroup_node.__class__.__name__ == 'colspec' and tgroup_node.get('colwidth') == 'auto':
                                tgroup_node['colwidth'] = 10000
                return value
            else:
                extract_from_paragraph = [
                    'paragraph',
                    'bullet_list',
                    'enumerated_list',
                    'definition_list',
                    'table',
                    'seealso',
                    'desc',
                    'math_block',
                    'literal_block',
                    'image'
                ]
                wrap_with_paragraph = [
                    'emphasis'
                ]
                result = self.docxbuilder_unwrap(value, class_names=extract_from_paragraph)

                target_class_names = ['list_item', 'definition', 'note']
                for target_class_name in target_class_names:
                    target_index_key = 'docxbuilder_fix_desc_content_' + target_class_name + '_index'
                    target_nodes = self.docutils_find_nodes(result, class_names=[target_class_name], index_key=target_index_key)
                    target_nodes.reverse()
                    for node in target_nodes:
                        node_parent = node.parent
                        if node_parent is None:
                            raise Exception("'node_parent' is 'None'")
                        target_index = node[target_index_key]
                        for child_index, child in enumerate(node_parent):
                            if child.__class__.__name__ == target_class_name and child[target_index_key] == target_index:
                                old_node = node_parent[child_index]
                                new_node = self.docxbuilder_unwrap(old_node, class_names=extract_from_paragraph)
                                node_parent[child_index] = new_node

                target_class_name = 'enumerated_list'
                target_index_key = 'docxbuilder_fix_desc_content_' + target_class_name + '_index'
                target_nodes = self.docutils_find_nodes(result, class_names=[target_class_name], index_key=target_index_key)
                target_nodes.reverse()
                for node in target_nodes:
                    node['enumtype'] = 'arabic'
                    node['prefix'] = ''
                    node['suffix'] = '.'
                    node['start'] = 1

                target_class_name = 'container'
                target_index_key = 'docxbuilder_fix_desc_content_' + target_class_name + '_index'
                target_nodes = self.docutils_find_nodes(result, class_names=[target_class_name], index_key=target_index_key)
                target_nodes.reverse()
                for node in target_nodes:
                    for child_index, child in enumerate(node):
                        if child.__class__.__name__ in wrap_with_paragraph:
                            paragraph = docutils.nodes.paragraph()
                            paragraph.append(child)
                            node[child_index] = paragraph

                return result
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e

    def docxbuilder_assemble_doctree(
        self,
        docxbuilder_self,
        master,
        toctree_only
    ):
        try:
            if self.__docxbuilder_assemble_doctree_log:
                self.__logger.info(f"-- {inspect.currentframe().f_code.co_name}")

            tree = self.__docxbuilder_old_assemble_doctree(docxbuilder_self, master, toctree_only)

            if self.__docxbuilder_assemble_doctree_log and self.__docxbuilder_assemble_doctree_log_before:
                self.__logger.info(f"-- {inspect.currentframe().f_code.co_name} log node before")
                self.docutils_log_node(tree)

            if self.__docxbuilder_assemble_doctree_log:
                self.__logger.info(f"-- {inspect.currentframe().f_code.co_name} find 'desc_content' nodes")

            class_names = ['section', 'desc_content', 'table']
            index_key = 'docxbuilder_new_assemble_doctree_index'
            nodes = self.docutils_find_nodes(tree, class_names=class_names, index_key=index_key)
            nodes.reverse()

            if self.__docxbuilder_assemble_doctree_log:
                self.__logger.info(f"-- {inspect.currentframe().f_code.co_name} found nodes len: '{len(nodes)}'")

            if self.__docxbuilder_assemble_doctree_log:
                self.__logger.info(f"-- {inspect.currentframe().f_code.co_name} process")

            for node_index, node in enumerate(nodes):
                if self.__docxbuilder_assemble_doctree_log:
                    self.__logger.info(f"-- {inspect.currentframe().f_code.co_name} process node {node_index + 1} of {len(nodes)}")

                node_parent = node.parent

                if node_parent is None:
                    raise Exception(f"node_parent is None")

                index_value = node[index_key]

                for child_index, child in enumerate(node_parent):
                    if (
                            child.__class__.__name__ in class_names
                            and child[index_key] == index_value
                    ):
                        old_node = node_parent[child_index]
                        new_node = self.docxbuilder_fix_node(old_node)
                        node_parent[child_index] = new_node

            if self.__docxbuilder_assemble_doctree_log and self.__docxbuilder_assemble_doctree_log_after:
                self.__logger.info(f"-- {inspect.currentframe().f_code.co_name} log node after")
                self.docutils_log_node(tree)

            return tree
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e

    def mlx_traceability_inspect_item(
        self,
        name: None | str | object,
        collection: None | MlxTraceableCollection | object,
        config: None | dict[str, list[str]] | object = None,
        warning_to_error: bool = True,
        log: bool = False
    ) -> None:
        try:
            if config is None:
                return

            if log:
                self.__logger.info(f"-- {inspect.currentframe().f_code.co_name} name: '{name}'")

            # check-input
            if name is None:
                self.log_message_as_warning_or_error(f"'name' is none.", warning_to_error)
            elif not isinstance(name, str):
                self.log_message_as_warning_or_error(f"'name' is not an instance of 'str'.", warning_to_error)

            if collection is None:
                self.log_message_as_warning_or_error(f"'collection' is none.", warning_to_error)
            elif not isinstance(collection, MlxTraceableCollection):
                self.log_message_as_warning_or_error(f"'collection' is not an instance of 'MlxTraceableCollection'.", warning_to_error)

            if config is None:
                self.log_message_as_warning_or_error(f"'config' is none.", warning_to_error)
            elif not isinstance(config, dict):
                self.log_message_as_warning_or_error(f"'config' is not an instance of 'dict'.", warning_to_error)

            # process
            item: None | MlxTraceableItem | object = collection.get_item(name)

            if item is None:
                self.log_message_as_warning_or_error(f"'item' is none.", warning_to_error)

            try:
                item.self_test()
            except MlxTraceabilityException as mlx_traceability_exception:
                self.log_message_as_warning_or_error(f"{mlx_traceability_exception}", warning_to_error)
                if warning_to_error:
                    raise mlx_traceability_exception

            item_dict: dict[str, object] = item.to_dict()
            item_id: str = item_dict['id']
            item_targets: dict[str, object] = item_dict.get('targets', dict())
            config_keys: set[str] = set(config.keys())

            if log:
                self.__logger.info(f"-- {inspect.currentframe().f_code.co_name} config keys: {config_keys}")

            while config_keys:
                prefix: str = config_keys.pop()
                if not item_id.startswith(prefix):
                    continue
                if log:
                    self.__logger.info(f"-- {inspect.currentframe().f_code.co_name} validate id: '{item_id}' targets: {item_targets}")
                types: list[str] = config[prefix]
                item_links: list[str] = []
                for k, v in item_targets.items():
                    if k in types:
                        item_links.extend(v)
                if len(item_links) < 1:
                    self.log_message_as_warning_or_error(f"'{item_id}' has no links with types: {types}", warning_to_error)
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e
