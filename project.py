import json
import sys
import inspect
import subprocess
import shutil
import logging
from logging import LoggerAdapter
from logging import getLogger as logging_get_logger
from logging.config import dictConfig as logging_config_dict
from argparse import ArgumentParser
from argparse import Namespace
from pathlib import Path
from fnmatch import fnmatch

class Project:
    """
    Project class.
    """
    __logger: None | LoggerAdapter = None
    __help_message: None | str = None
    __subprocess_timeout: None | int = None
    __commands: None | list[str] = None
    __project_dir: str = Path(__file__).parent.absolute().as_posix()

    def __init__(
        self,
        help_message: None | str | object,
        namespace: None | Namespace | object,
        logger: None | LoggerAdapter | object = None
    ) -> None:
        try:
            if logger is not None and isinstance(logger, LoggerAdapter):
                self.__logger = logger
            else:
                self.__logger = logging_get_logger('.'.join([self.__module__, self.__class__.__name__]))

            self.__help_message = help_message

            if namespace is not None:
                self.__subprocess_timeout = namespace.subprocess_timeout if namespace.subprocess_timeout > 0 else None
                self.__commands = [namespace.commands] if isinstance(namespace.commands, str) else namespace.commands
        except Exception as e:
            if self.__logger: self.__logger.error(e, exc_info=True)
            raise e

    def help(self) -> None:
        try:
            self.__logger.info(self.__help_message)
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e

    def env(self) -> None:
        try:
            project_dir: str = Path(self.__project_dir).as_posix()
            build_dir: str = Path(project_dir).joinpath('build').as_posix()
            env_dir: str = Path(build_dir).joinpath('env').as_posix()

            self.__logger.info(f"-- [{inspect.currentframe().f_code.co_name}]: bgn")

            # create env
            cmd: list[str] = [
                sys.executable,
                '-m', 'venv',
                env_dir
            ]
            self.__logger.info(f"-- [{inspect.currentframe().f_code.co_name}] execute: {cmd}")
            subprocess.run(
                cmd,
                cwd=project_dir,
                text=True,
                check=True,
                capture_output=False,
                timeout=self.__subprocess_timeout
            )

            # install dependencies
            requirements_content: str = Path(project_dir).joinpath('doc', 'rst', 'sphinx', 'requirements.txt').read_bytes().decode()
            requirements_file: str = Path(env_dir).joinpath('requirements.txt').as_posix()
            Path(requirements_file).write_bytes(requirements_content.encode())
            python_file: str = self._find_python(dir=env_dir)
            cmd = [
                python_file,
                '-m', 'pip', 'install',
                '--trusted-host', 'pypi.org',
                '--trusted-host', 'pypi.python.org',
                '--trusted-host', 'files.pythonhosted.org',
                '-r', requirements_file
            ]
            self.__logger.info(f"-- [{inspect.currentframe().f_code.co_name}] execute: {cmd}")
            subprocess.run(
                cmd,
                cwd=project_dir,
                text=True,
                check=True,
                capture_output=False,
                timeout=self.__subprocess_timeout
            )

            self.__logger.info(f"-- [{inspect.currentframe().f_code.co_name}]: end")
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e

    def clean_env(self) -> None:
        try:
            project_dir: str = Path(self.__project_dir).as_posix()
            build_dir: str = Path(project_dir).joinpath('build').as_posix()
            env_dir: str = Path(build_dir).joinpath('env').as_posix()

            if not Path(env_dir).exists():
                return None

            self.__logger.info(f"-- [{inspect.currentframe().f_code.co_name}]: bgn")

            shutil.rmtree(env_dir)

            self.__logger.info(f"-- [{inspect.currentframe().f_code.co_name}]: end")
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e

    def doc_example_enumerated_list(self) -> None:
        try:
            project_dir: str = Path(self.__project_dir).as_posix()
            build_dir: str = Path(project_dir).joinpath('build').as_posix()
            env_dir: str = Path(build_dir).joinpath('env').as_posix()
            subproject: str = 'example-enumerated-list'
            builder: str = 'docx'

            self.__logger.info(f"-- [{inspect.currentframe().f_code.co_name}]: bgn")

            python_file: str = self._find_python(dir=env_dir)
            subprocess.run(
                [
                    python_file, '-m', 'sphinx',
                    '-E',
                    '-w', f'build/doc/{subproject}/{builder}/sphinx-warnings.txt',
                    '-D', f'project_builder={builder}',
                    '-D', f'project_subprojects={subproject}',
                    '-b', builder,
                    'doc/rst/sphinx',
                    f'build/doc/{subproject}/{builder}'
                ],
                cwd=project_dir,
                text=True,
                check=True,
                capture_output=False,
                timeout=self.__subprocess_timeout
            )

            self.__logger.info(f"-- [{inspect.currentframe().f_code.co_name}]: end")
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e

    def doc_example_enumerated_list_hierarchical(self) -> None:
        try:
            project_dir: str = Path(self.__project_dir).as_posix()
            build_dir: str = Path(project_dir).joinpath('build').as_posix()
            env_dir: str = Path(build_dir).joinpath('env').as_posix()
            subproject: str = 'example-enumerated-list-hierarchical'
            builder: str = 'docx'

            self.__logger.info(f"-- [{inspect.currentframe().f_code.co_name}]: bgn")

            python_file: str = self._find_python(dir=env_dir)
            subprocess.run(
                [
                    python_file, '-m', 'sphinx',
                    '-E',
                    '-w', f'build/doc/{subproject}/{builder}/sphinx-warnings.txt',
                    '-D', f'project_builder={builder}',
                    '-D', f'project_subprojects={subproject}',
                    '-b', builder,
                    'doc/rst/sphinx',
                    f'build/doc/{subproject}/{builder}'
                ],
                cwd=project_dir,
                text=True,
                check=True,
                capture_output=False,
                timeout=self.__subprocess_timeout
            )

            self.__logger.info(f"-- [{inspect.currentframe().f_code.co_name}]: end")
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e

    def doc(self) -> None:
        try:
            self.__logger.info(f"-- [{inspect.currentframe().f_code.co_name}]: bgn")

            self.doc_example_enumerated_list()
            self.doc_example_enumerated_list_hierarchical()

            self.__logger.info(f"-- [{inspect.currentframe().f_code.co_name}]: end")
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e

    def clean_doc(self) -> None:
        try:
            project_dir: str = Path(self.__project_dir).as_posix()
            build_dir: str = Path(project_dir).joinpath('build').as_posix()
            doc_dir: str = Path(build_dir).joinpath('doc').as_posix()

            if not Path(doc_dir).exists():
                return None

            self.__logger.info(f"-- [{inspect.currentframe().f_code.co_name}]: bgn")

            shutil.rmtree(doc_dir)

            self.__logger.info(f"-- [{inspect.currentframe().f_code.co_name}]: end")
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e

    def package(self) -> None:
        try:
            project_dir: str = Path(self.__project_dir).as_posix()
            project_json_file: str = Path(project_dir).joinpath('project.json').as_posix()
            build_dir: str = Path(project_dir).joinpath('build').as_posix()
            env_dir: str = Path(build_dir).joinpath('env').as_posix()
            package_dir: str = Path(build_dir).joinpath('package').as_posix()
            dist_dir: str = Path(build_dir).joinpath('dist').as_posix()
            include_patterns: set[str] = {
                '*'
            }
            exclude_patterns: set[str] = {
                'doc/rst/sphinx/requirements.txt',
                '*.py'
            }
            copy_files: list[tuple[str, str]] = []

            self.__logger.info(f"-- [{inspect.currentframe().f_code.co_name}]: bgn")

            # create package
            if not Path(project_json_file).exists():
                raise Exception(f"not exists: '{project_json_file}'")

            project_json: dict[str, object] = json.loads(Path(project_json_file).read_bytes().decode())
            package_name: None | str = project_json.get('name', None)

            if package_name is None:
                raise Exception(f"'package_name' is None")

            package_version: None | str = project_json.get('version', None)

            if package_version is None:
                raise Exception(f"'package_version' is None")

            dst_dir: str = Path(package_dir).joinpath('src', package_name.replace('-', '/')).as_posix()

            for v in Path(project_dir).joinpath('doc', 'rst', 'sphinx').rglob('*'):
                if not v.is_file():
                    continue
                file: str = v.as_posix()
                file_relative: str = Path(file).relative_to(project_dir).as_posix()
                file_add: bool = False
                for include_pattern in include_patterns:
                    if fnmatch(file_relative, include_pattern):
                        file_add = True
                        break
                if not file_add:
                    continue
                for exclude_pattern in exclude_patterns:
                    if fnmatch(file_relative, exclude_pattern):
                        file_add = False
                        break
                if not file_add:
                    continue
                copy_files.append(
                    (
                        file,
                        Path(dst_dir).joinpath(Path(file).relative_to(Path(project_dir).joinpath('doc', 'rst', 'sphinx')).as_posix()).as_posix()
                    )
                )

            if Path(package_dir).exists():
                shutil.rmtree(package_dir)

            if Path(dist_dir).exists():
                shutil.rmtree(dist_dir)

            for src_file, dst_file in copy_files:
                if not Path(src_file).exists():
                    raise Exception(f"not exists: '{src_file}'")
                info_src: str = Path(src_file).relative_to(project_dir).as_posix()
                info_dst: str = Path(dst_file).relative_to(Path(package_dir).joinpath('src')).as_posix()
                self.__logger.info(f"-- [{inspect.currentframe().f_code.co_name}]: add: '{info_src}' as: '{info_dst}'")
                Path(dst_file).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src_file, dst_file)

            pyproject_toml: str = '\n'.join([
                '[build-system]',
                'requires = ["pdm-backend"]',
                'build-backend = "pdm.backend"',
                '',
                '[project]',
                f'name = "{package_name}"',
                f'version = "{package_version}"',
                'description = "Exqudens Sphinx Doc Example"',
                'requires-python = ">=3"',
                '',
                '[tool.pdm.build]',
                'includes = ["src"]',
                'package-dir = "src"',
                ''
            ])

            Path(package_dir).mkdir(parents=True, exist_ok=True)
            Path(package_dir).joinpath('pyproject.toml').write_bytes(pyproject_toml.encode())

            python_file: str = self._find_python(dir=env_dir)
            cmd = [
                python_file,
                '-m', 'pip', 'wheel',
                '--no-deps',
                '-w', dist_dir,
                '--trusted-host', 'pypi.org',
                '--trusted-host', 'pypi.python.org',
                '--trusted-host', 'files.pythonhosted.org',
                '.'
            ]
            self.__logger.info(f"-- [{inspect.currentframe().f_code.co_name}] execute: {cmd}")
            subprocess.run(
                cmd,
                cwd=package_dir,
                text=True,
                check=True,
                capture_output=False,
                timeout=self.__subprocess_timeout
            )

            self.__logger.info(f"-- [{inspect.currentframe().f_code.co_name}]: end")
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e

    def clean_package(self) -> None:
        try:
            project_dir: str = Path(self.__project_dir).as_posix()
            build_dir: str = Path(project_dir).joinpath('build').as_posix()
            dist_dir: str = Path(build_dir).joinpath('dist').as_posix()

            if not Path(dist_dir).exists():
                return None

            self.__logger.info(f"-- [{inspect.currentframe().f_code.co_name}]: bgn")

            shutil.rmtree(dist_dir)

            self.__logger.info(f"-- [{inspect.currentframe().f_code.co_name}]: end")
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e

    def clean(self) -> None:
        try:
            self.__logger.info(f"-- [{inspect.currentframe().f_code.co_name}]: bgn")

            self.clean_package()
            self.clean_doc()
            self.clean_env()

            self.__logger.info(f"-- [{inspect.currentframe().f_code.co_name}]: end")
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e

    def _run(self) -> int:
        try:
            for command in self.__commands:
                method = getattr(self, command)
                if not method:
                    raise Exception(f"command not found: '{command}'")
                method()
            return 0
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e

    def _find_python(self, dir: None | str | object) -> str:
        try:
            if dir is None:
                raise Exception("'dir' is none")
            if not isinstance(dir, str):
                raise Exception("'dir' is not an instance of 'str'")
            if len(dir) == 0:
                raise Exception("'dir' is empty")
            if not Path(dir).exists():
                raise Exception(f"not exists: '{dir}'")
            if not Path(dir).is_dir():
                raise Exception(f"is not a directory: '{dir}'")

            if Path(dir).joinpath('Scripts', 'python.exe').exists():
                return Path(dir).joinpath('Scripts', 'python.exe').as_posix()
            elif Path(dir).joinpath('bin', 'python').exists():
                return Path(dir).joinpath('bin', 'python').as_posix()
            else:
                raise Exception(f"unexpected condition")
        except Exception as e:
            self.__logger.error(e, exc_info=True)
            raise e

if __name__ == '__main__':
    logger: None | LoggerAdapter = None
    try:
        sys_argv: None | list[str] | object = sys.argv[1:]
        avilable_commands: list[str] = [name for name, _ in inspect.getmembers(Project, predicate=inspect.isfunction) if not name.startswith('_')]
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
            '-st', '--subprocess-timeout',
            nargs='?',
            type=int,
            default=0,
            help=f"subprocess timeout in seconds (default: %(default)s)"
        )
        parser.add_argument(
            'commands',
            nargs='*',
            type=str,
            choices=avilable_commands,
            default='help',
            help='commands (default: %(default)s)'
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
        project: Project = Project(
            help_message=parser.format_help(),
            namespace=namespace,
            logger=logger
        )
        raise SystemExit(project._run())
    except Exception as e:
        if logger: logger.error(e, exc_info=True)
        raise e
    except SystemExit as e:
        raise e
