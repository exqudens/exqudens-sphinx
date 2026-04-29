from logging import LoggerAdapter
from logging import LogRecord
from logging import getLogger as logging_get_logger
from collections import deque

# sphinx
from sphinx.application import Sphinx
from sphinx.util.logging import WarningSuppressor
from sphinx.util._io import TeeStripANSI

class ConfUtil:
    """
    ConfUtil class.
    """
    __logger: None | LoggerAdapter = None

    __sphinx_warnings_file: None | str = None
    __sphinx_warnings: None | deque[LogRecord] = None
    __sphinx_old_util_logging_warning_suppressor_filter = None
    __sphinx_new_util_logging_warning_suppressor_filter = None

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
        sphinx_util_logging_warning_suppressor_filter_override: bool = True
    ) -> None:
        try:
            if sphinx_application is None:
                raise Exception("'sphinx_application' is none!")
            elif not isinstance(sphinx_application, Sphinx):
                raise Exception(f"'sphinx_application' is not an instance of 'Sphinx' it is instance of '{type(sphinx_application)}'")

            if sphinx_application._warning is not None and isinstance(sphinx_application._warning, TeeStripANSI):
                self.__sphinx_warnings_file = sphinx_application._warning.stream_file.name

            if sphinx_util_logging_warning_suppressor_filter_override:
                self.__sphinx_warnings = deque([])
                self.__sphinx_old_util_logging_warning_suppressor_filter = getattr(WarningSuppressor, 'filter')
                self.__sphinx_new_util_logging_warning_suppressor_filter = lambda sphinx_self, record: self.sphinx_util_logging_warning_suppressor_filter(sphinx_self, record)
                setattr(WarningSuppressor, 'filter', self.__sphinx_new_util_logging_warning_suppressor_filter)
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
                try:
                    record_message = record.msg % record.args
                except (TypeError, ValueError):
                    record_message = record.msg  # use record.msg itself
                entry: dict[str, str] = {
                    'location': str(record_location),
                    'levelname': str(record_levelname),
                    'message': str(record_message)
                }
                result.append(entry)
            return result
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
