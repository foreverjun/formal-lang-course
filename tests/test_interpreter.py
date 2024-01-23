import io
from contextlib import redirect_stdout

from project.parser.interpreter.interpreter import InterpreterVisitor
from project.parser.parser import check, get_parser

test = [
    ("val a = true; print a ;", {"True\n"}),
    ("val c = {1,2,3} ; print c ;", {"{1, 2, 3}\n"}),
    ("""val c = "Hello World" ; print c ;""", {"Hello World\n"}),
    (
        """val b = load_graph( "atom") ; val nb = set_start({1,2,3}, b) ; val k = get_start(nb) ; print k;""",
        {"{1, 2, 3}\n"},
    ),
    (
        """val b = load_graph( "atom") ; val nb = set_final({1,2,3}, b) ; val k = get_final(nb) ; print k;""",
        {"{1, 2, 3}\n"},
    ),
    (
        """val t = regex( "a.b" ); val l = get_labels(t); print l ;""",
        {"{a, b}\n", "{b, a}\n"},
    ),
    ("""val k = 1 ; val t = k in {3,2}; print t ;""", {"False\n"}),
    (
        """val t = {1, 5} ; val m = map([i -> i in { 4, 5} ], t); print m ;""",
        {"{False, True}\n"},
    ),
    (
        """val t = {1,2,3,4,5} ; val m = filter([i ->  not (i in {1, 5})], t); print m ;""",
        {"{2, 3, 4}\n"},
    ),
    (
        """val m = {(1,2), (2,3), (3,4), (4,5)} ; val k = map([ (c,d) -> (d,c)], m); print k ;""",
        {"{(3, 2), (5, 4), (2, 1), (4, 3)}\n"},
    ),
    (
        """val m = {(1,2), (2,3), (3,4), (4,5)} ; val k = filter([ (c,d) -> c in {1, 2}], m); print k ;""",
        {"{(2, 3), (1, 2)}\n"},
    ),
    (
        """val d  = { (1,2,3), (4,5,6) } ; val s = map([ (a,b,c) -> (a,b)], d); print s ;""",
        {"{(4, 5), (1, 2)}\n"},
    ),
]


def test_interpreter():
    for code, expected in test:
        parser = get_parser(code)
        tree = parser.prog()
        assert check(code)
        visitor = InterpreterVisitor()
        f = io.StringIO()
        with redirect_stdout(f):
            visitor.visit(tree)
        s = f.getvalue()
        assert s in expected
