from pathlib import Path
from project.parser.interpreter.interpreter import InterpreterVisitor
from project.parser.parser import get_parser, check


def interpret_file(file_path: Path):
    with open(file_path, "r") as f:
        code = f.read()
    parser = get_parser(code)
    tree = parser.prog()
    if not check(code):
        raise RuntimeError("Invalid code")
    visitor = InterpreterVisitor()
    visitor.visit(tree)
    return visitor.output
