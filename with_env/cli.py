import os
import shutil
import sys

import dotenv


def cli():
    has_set_anything = dotenv.load_dotenv(
        ".env",
        verbose=True,
        override=True,
        interpolate=False
    )

    if not has_set_anything:
        print("with-env: .env not found", file=sys.stderr)

    argv = sys.argv[1:]
    program = argv[0]

    program_path = shutil.which(program)
    if program_path is None:
        print(f"{program}: not found")
        exit(1)

    os.execve(program_path, argv, os.environ)
