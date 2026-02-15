import sys
from typing import List, Sequence

import click

from .execute import ProgramExecutor, RestartableProgramExecutor
from .watch import FileObserver


def _remove_duplicates(items: Sequence[str]) -> List[str]:
    seen = set()
    uniques = []

    for item in items:
        if item not in seen:
            seen.add(item)
            uniques.append(item)
        else:
            print(f"with-env: {item}: specified multiple times", file=sys.stderr)

    return uniques


@click.command(context_settings={"allow_interspersed_args": False})
@click.option("--watch", "-w", "watch_for_changes", is_flag=True, help="Watch for changes in the .env and restart the command.")
@click.option("--file", "-f", "extra_env_files", multiple=True, help="Specify additional .env files to load.")
@click.option("--profile", "-p", "profiles", multiple=True, help="Specify profiles to load corresponding .env.{profile} files (processed after --file options).")
@click.argument("argv", nargs=-1, required=True)
def cli(
    watch_for_changes: bool,
    extra_env_files: List[str],
    profiles: List[str],
    argv: List[str],
):
    env_files = [
        ".env",
        *extra_env_files,
    ]

    for profile in profiles:
        env_files.append(f".env.{profile}")

    env_files = _remove_duplicates(env_files)

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
