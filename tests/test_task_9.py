from networkx import MultiDiGraph
from pyformlang.cfg import CFG

from project.task_9 import cfpq_matrices


def test_1():
    graph = MultiDiGraph()
    graph.add_edges_from(
        [
            (0, 1, {"label": "a"}),
            (1, 2, {"label": "b"}),
            (2, 3, {"label": "a"}),
            (3, 4, {"label": "b"}),
            (0, 5, {"label": "b"}),
            (5, 6, {"label": "a"}),
            (6, 7, {"label": "b"}),
        ]
    )
    text = """
    S -> A B | B A | A A | B B
    A -> a
    B -> b
    """
    cfg = CFG.from_text(text)
    assert cfpq_matrices(graph, cfg) == {(2, 4), (5, 7), (0, 6), (0, 2), (1, 3)}


def test_2():
    #     anbn
    text = """
S -> A
A -> a A b | a b
    """
    cfg = CFG.from_text(text)
    graph = MultiDiGraph()
    graph.add_edges_from(
        [
            (0, 1, {"label": "a"}),
            (1, 2, {"label": "a"}),
            (2, 3, {"label": "a"}),
            (3, 4, {"label": "b"}),
            (4, 5, {"label": "b"}),
            (5, 6, {"label": "b"}),
        ]
    )
    assert cfpq_matrices(graph, cfg) == {(0, 6), (1, 5), (2, 4)}


def test_3():
    # correct brackets sequence
    text = """
    S -> S S | a S b | a b
    """
    cfg = CFG.from_text(text)
    graph = MultiDiGraph()
    graph.add_edges_from(
        [
            (0, 1, {"label": "a"}),
            (1, 2, {"label": "a"}),
            (2, 3, {"label": "a"}),
            (3, 4, {"label": "b"}),
            (4, 5, {"label": "b"}),
            (5, 6, {"label": "b"}),
            (1, 7, {"label": "b"}),
            (2, 8, {"label": "b"}),
            (8, 9, {"label": "a"}),
            (9, 10, {"label": "b"}),
        ]
    )
    assert cfpq_matrices(graph, cfg) == {
        (0, 7),
        (2, 4),
        (1, 5),
        (1, 8),
        (8, 10),
        (0, 6),
        (1, 10),
    }
