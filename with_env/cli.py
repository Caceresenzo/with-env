import click

from .execute import ProgramExecutor, RestartableProgramExecutor
from .watch import FileObserver


@click.command(context_settings={"allow_interspersed_args": False})
@click.option("--watch", "-w", "watch_for_changes", is_flag=True, help="Watch for changes in the .env and restart the command.")
@click.argument("argv", nargs=-1)
def cli(
    watch_for_changes: bool,
    argv: list[str],
):
    env_files = [
        ".env",
    ]

    if watch_for_changes:
        executor = RestartableProgramExecutor(argv, env_files)
        observer = FileObserver(executor)

        executor.start()
        observer.run(env_files)
    else:
        ProgramExecutor(argv, env_files).start()
