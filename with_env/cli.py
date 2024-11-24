import os
import shutil
import sys

import dotenv


def cli():
    dotenv.load_dotenv()

    argv = sys.argv[1:]
    program = argv[0]

    program_path = shutil.which(program)
    if program_path is None:
        print(f"{program}: not found")
        exit(1)

    os.execv(program_path, argv)
