import pydot
from antlr4 import (
    ParserRuleContext,
    TerminalNode,
    InputStream,
    CommonTokenStream,
    ParseTreeWalker,
    ErrorNode,
)

from project.parser.languageLexer import languageLexer
from project.parser.languageListener import languageListener
from project.parser.languageParser import languageParser


class ParsingException(Exception):
    "Raised when parsing error occurs"
    pass


class CheckTreeListener(languageListener):
    def visitErrorNode(self, node: ErrorNode):
        raise ParsingException(f"Error at {node}")


class DotTreeListener(languageListener):
    def __init__(self):
        self.dot = pydot.Dot("code", strict=True)
        self._curr = 0
        self._stack = []

    def enterEveryRule(self, ctx: ParserRuleContext):
        self.dot.add_node(
            pydot.Node(self._curr, label=languageParser.ruleNames[ctx.getRuleIndex()])
        )
        if len(self._stack) > 0:
            self.dot.add_edge(pydot.Edge(self._stack[-1], self._curr))
        self._stack.append(self._curr)
        self._curr += 1

    def exitEveryRule(self, ctx: ParserRuleContext):
        self._stack.pop()

    def visitTerminal(self, node: TerminalNode):
        self.dot.add_node(pydot.Node(self._curr, label=f"'{node}'"))
        self.dot.add_edge(pydot.Edge(self._stack[-1], self._curr))
        self._curr += 1


def get_parser(code: str) -> languageParser:
    lexer = languageLexer(InputStream(code))
    stream = CommonTokenStream(lexer)
    parser = languageParser(stream)
    return parser


def check(code: str) -> bool:
    parser = get_parser(code)
    parser.removeErrorListeners()
    listener = CheckTreeListener()
    walker = ParseTreeWalker()
    try:
        walker.walk(listener, parser.prog())
    except ParsingException:
        return False
    return parser.getNumberOfSyntaxErrors() == 0


def save_dot(code: str, filename: str) -> None:
    parser = get_parser(code)
    if parser.getNumberOfSyntaxErrors() > 0:
        raise ParsingException("Syntax error")

    listener = DotTreeListener()
    walker = ParseTreeWalker()

    walker.walk(listener, parser.prog())
    listener.dot.write(filename)
