import click
import sys

from .execute import ProgramExecutor, RestartableProgramExecutor
from .watch import FileObserver


@click.command(context_settings={"allow_interspersed_args": False})
@click.option("--watch", "-w", "watch_for_changes", is_flag=True, help="Watch for changes in the .env and restart the command.")
@click.argument("argv", nargs=-1)
def cli(
    watch_for_changes: bool,
    argv: list[str],
):
    env_files = set([
        ".env",
    ])

    while len(argv) and argv[0].startswith(":"):
        if isinstance(argv, tuple):
            argv = list(argv)

        profile = argv.pop(0)[1:]
        env_files.add(f".env.{profile}")

    if not len(argv):
        print(f"with-env: no command specified", file=sys.stderr)
        exit(1)

    if watch_for_changes:
        executor = RestartableProgramExecutor(argv, env_files)
        observer = FileObserver(executor)

        executor.start()
        observer.run(env_files)
    else:
        ProgramExecutor(argv, env_files).start()
