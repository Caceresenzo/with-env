import os
import shutil
import signal
import sys
import typing

import dotenv


class ProgramExecutor:

    def __init__(
        self,
        argv: typing.List[str],
        env_files: typing.List[str],
    ):
        self._argv = argv
        self._env_files = env_files

    @property
    def env_files(self):
        return self._env_files

    def start(self):
        for env_file in self._env_files:
            if not os.path.exists(env_file):
                print(f"with-env: {env_file}: not found", file=sys.stderr)
                continue

            has_set_anything = dotenv.load_dotenv(
                env_file,
                verbose=True,
                override=True,
                interpolate=False
            )

            if not has_set_anything:
                print(f"with-env: {env_file}: empty", file=sys.stderr)

        argv = self._argv
        program = argv[0]

        program_path = shutil.which(program)
        if program_path is None:
            print(f"with-env: {program}: not found", file=sys.stderr)
            exit(1)

        try:
            os.execve(program_path, argv, os.environ)
        except BaseException as exception:
            print(f"with-env: {program}: {exception}", file=sys.stderr)

        exit(1)


class RestartableProgramExecutor(ProgramExecutor):

    def __init__(
        self,
        argv: typing.List[str],
        env_files: typing.List[str],
    ):
        super().__init__(argv, env_files)

        self.child_pid = None

    def start(self):
        if self.child_pid:
            os.kill(self.child_pid, signal.SIGKILL)
            os.waitpid(self.child_pid, 0)

        self.child_pid = os.fork()
        if not self.child_pid:
            super().start()
