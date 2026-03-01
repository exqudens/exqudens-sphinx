import json
import inspect
import shutil
import sys
import logging
from logging import LoggerAdapter
from logging import getLogger as logging_get_logger
from logging.config import dictConfig as logging_config_dict
from typing import Callable
from pathlib import Path
from argparse import ArgumentParser
from argparse import Namespace

class WarningUtil:
    """
    WarningUtil class.
    """
    __logger: None | LoggerAdapter = None
    __filters: None | list[tuple[Callable[[dict[str, str]], bool], int]] = None
    __filters_state: None | list[bool] = None

    def __init__(
        self,
        logger: None | LoggerAdapter | object = None
    ) -> None:
        try:
            if logger is not None and isinstance(logger, LoggerAdapter):
                self.__logger = logger
            else:
                self.__logger = logging_get_logger('.'.join([__class__.__module__, __class__.__name__]))
            self.__filters = self.__create_filters()
            self.__filters_state = [True] * len(self.__filters)
        except Exception as e:
            if self.__logger: self.__logger.error(e, exc_info=True)
            raise e

    def get_filters_size(self) -> int:
        try:
            return len(self.__filters)
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e

    def enable_filter(self, *filter_ids) -> None:
        try:
            # check input
            for filter_id in filter_ids:
                if filter_id is None:
                    raise Exception(f"'filter_id' is none")
                elif not isinstance(filter_id, int):
                    raise Exception(f"'filter_id' is not an instance of 'int'")
                elif filter_id < 0 or filter_id >= len(self.__filters):
                    raise Exception(f"invalid 'filter_id': {filter_id} filters size: {len(self.__filters)}")

            # process
            for filter_id in filter_ids:
                self.__logger.info(f"-- {inspect.currentframe().f_code.co_name} filter_id: {filter_id}")
                self.__filters_state[filter_id] = True
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e

    def disable_filter(self, *filter_ids) -> None:
        try:
            # check input
            for filter_id in filter_ids:
                if filter_id is None:
                    raise Exception(f"'filter_id' is none")
                elif not isinstance(filter_id, int):
                    raise Exception(f"'filter_id' is not an instance of 'int'")
                elif filter_id < 0 or filter_id >= len(self.__filters):
                    raise Exception(f"invalid 'filter_id': {filter_id} filters size: {len(self.__filters)}")

            # process
            for filter_id in filter_ids:
                self.__logger.info(f"-- {inspect.currentframe().f_code.co_name} filter_id: {filter_id}")
                self.__filters_state[filter_id] = False
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e

    def check_warnings(
        self,
        input: None | list[dict[str, str]] | object = None,
        file: None | str | object = None
    ) -> None:
        try:
            # check input
            if input is None:
                raise Exception(f"'input' is none")
            elif not isinstance(input, list):
                raise Exception(f"'input' is not an instance of 'list'")
            elif len(input) < 1:
                return None

            if file is not None and not isinstance(file, str):
                raise Exception(f"'file' is not an instance of 'str'")
            elif file is not None and len(file) < 1:
                raise Exception(f"'file' is emty")

            # process
            self.__logger.info(f"-- {inspect.currentframe().f_code.co_name} input.size: {len(input)}")

            if file is not None:
                warnings_json: str = json.dumps(input, indent=4)
                warnings_json_file: str = Path(file).parent.joinpath(f"{Path(file).stem}.json").as_posix()
                Path(warnings_json_file).absolute().parent.mkdir(parents=True, exist_ok=True)
                Path(warnings_json_file).absolute().write_bytes(warnings_json.encode())

            filtered: dict[int, list[dict[str, str]]] = {}

            for input_entry in input:
                filter_id: int = -1
                exclude: bool = False
                warning: dict[str, str] = input_entry
                for filters_index, filters_tuple in enumerate(self.__filters):
                    filter: Callable[[dict[str, str]], bool] = filters_tuple[0]
                    exclude = self.__filters_state[filters_index] and filter(warning)
                    if exclude:
                        filter_id = filters_index
                        break
                if filter_id not in filtered:
                    filtered[filter_id] = []
                filtered[filter_id].append(warning)

            filtered = dict(sorted(filtered.items()))

            filtered_count: dict[int, int] = {}

            if file is not None:
                warnings_json_dir: str = Path(file).parent.joinpath(Path(file).stem).as_posix()
                if Path(warnings_json_dir).exists():
                    shutil.rmtree(warnings_json_dir)

            for filter_id in filtered:
                if file is not None:
                    warnings_json: str = json.dumps(filtered[filter_id], indent=4)
                    warnings_json_file: str = Path(warnings_json_dir).joinpath(f"filter-{filter_id}-{Path(file).stem}.json").as_posix()
                    Path(warnings_json_file).absolute().parent.mkdir(parents=True, exist_ok=True)
                    Path(warnings_json_file).absolute().write_bytes(warnings_json.encode())
                count: int = len(filtered[filter_id])
                filtered_count[filter_id] = count
                self.__logger.info(f"-- [{inspect.currentframe().f_code.co_name}] filter: {filter_id} amount: {count}")

            filtered_count = dict(sorted(filtered_count.items()))

            for filter_id in filtered_count:
                expected_max_count: int = self.__filters[filter_id][1]
                actual_count: int = filtered_count[filter_id]
                if actual_count > expected_max_count:
                    warnings_json: str = json.dumps(filtered[filter_id], indent=4)
                    raise Exception(f"unexpected count: {actual_count} for filter id: {filter_id} expected mac count: {expected_max_count} warnings: {warnings_json}")
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e

    def __string_filter(
        self,
        input: None | str | object,
        startswith: None | list[str] | object = None,
        contains: None | list[str] | object = None,
        endswith: None | list[str] | object = None
    ) -> bool:
        try:
            # check input
            if input is None:
                raise Exception(f"'input' is none")
            elif not isinstance(input, str):
                raise Exception(f"'input' is not an instance of 'list'")

            if startswith is not None and not isinstance(startswith, list):
                raise Exception(f"'startswith' is not an instance of 'list'")
            elif startswith is not None and len(startswith) < 1:
                raise Exception(f"'startswith' is emty")

            if contains is not None and not isinstance(contains, list):
                raise Exception(f"'contains' is not an instance of 'list'")
            elif contains is not None and len(contains) < 1:
                raise Exception(f"'contains' is emty")

            if endswith is not None and not isinstance(endswith, list):
                raise Exception(f"'endswith' is not an instance of 'list'")
            elif endswith is not None and len(endswith) < 1:
                raise Exception(f"'endswith' is emty")

            # process
            if startswith is not None:
                startswith_result: bool = False
                for v in startswith:
                    if input.startswith(v):
                        startswith_result = True
                        break
                if not startswith_result:
                    return False

            if endswith is not None:
                endswith_result: bool = False
                for v in endswith:
                    if input.endswith(v):
                        endswith_result = True
                        break
                if not endswith_result:
                    return False

            if contains is None:
                return True

            contains_copy: list[str] = list(contains)
            input_copy: str = str(input)

            while contains_copy:
                target: str = contains_copy.pop(0)
                found_index: int = input_copy.find(target)
                if found_index < 0:
                    return False
                input_copy = input_copy[found_index + len(target):]

            return True
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e

    def __create_filters(self) -> list[tuple[Callable[[dict[str, str]], bool], int]]:
        try:
            def filter_0(input: dict[str, str]) -> bool:
                input_location: str = input.get('location', '')
                input_levelname: str = input.get('levelname', '')
                input_message: str = input.get('message', '')
                valid_location: bool = input_location is not None
                valid_levelname: bool = input_levelname is not None
                valid_message: bool = input_message.startswith("toctree contains reference to nonexisting document")
                return valid_location and valid_levelname and valid_message

            def filter_last(input: dict[str, str]) -> bool:
                return True

            return [
                (filter_0, sys.maxsize),
                (filter_last, 0)
            ]
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e

if __name__ == '__main__':
    logger: None | LoggerAdapter = None
    try:
        sys_argv: None | list[str] | object = sys.argv[1:]
        parser: ArgumentParser = ArgumentParser()
        parser.add_argument(
            '-ll', '--log-level',
            nargs='?',
            type=str,
            choices=[
                logging.getLevelName(logging.DEBUG),
                logging.getLevelName(logging.INFO),
                logging.getLevelName(logging.WARNING),
                logging.getLevelName(logging.ERROR),
                logging.getLevelName(logging.FATAL)
            ],
            default=logging.getLevelName(logging.DEBUG),
            help=f"log level (default: %(default)s)"
        )
        parser.add_argument(
            'input_file',
            type=str,
            help='Input file path'
        )
        namespace: Namespace = parser.parse_args(sys_argv)
        logging_config_dict({
            'version': 1,
            'formatters': {
                'formatter': {
                    'format': '%(message)s' # '%(asctime)s %(levelname)-4.4s [%(threadName)s] %(name)s %(funcName)s(%(filename)s:%(lineno)d): %(message)s'
                }
            },
            'handlers': {
                'handler': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'formatter',
                    'stream': 'ext://sys.stdout'
                }
            },
            'loggers': {
                'root': {
                    'level': logging.getLevelName(namespace.log_level),
                    'handlers': ['handler']
                }
            }
        })
        logger = logging_get_logger()
        input_file: None | str | object = namespace.input_file
        if input_file is None:
            raise Exception("'input_file' is none")
        elif not isinstance(input_file, str):
            raise Exception(f"'input_file' is not an instance of 'str'")
        elif len(input_file) < 1:
            raise Exception(f"'input_file' is emty")
        logger.info(f"-- [{inspect.currentframe().f_code.co_name}]: bgn")
        obj: WarningUtil = WarningUtil(logger=logger)
        input_json: str = Path(input_file).read_bytes().decode()
        input: list[dict[str, str]] = json.loads(input_json)
        obj.check_warnings(
            input=input,
            file=Path(input_file).parent.joinpath(f"{Path(input_file).stem}.txt").as_posix()
        )
        logger.info(f"-- [{inspect.currentframe().f_code.co_name}]: end")
        raise SystemExit(0)
    except Exception as e:
        if logger: logger.error(e, exc_info=True)
        raise e
    except SystemExit as e:
        raise e
