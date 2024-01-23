from sys import argv
from pathlib import Path

from project.parser.interpreter.cli import interpret_file

if __name__ == "__main__":
    if len(argv) < 2:
        raise RuntimeError("No file provided")
    file_path = Path(argv[1])
    print(interpret_file(file_path))
