from typing import List, Tuple, Set

from networkx import MultiDiGraph
from pyformlang.cfg import CFG, Variable, Terminal

from project.task_6 import cfg_to_weak_cnf


def hellings(cfg: CFG, graph: MultiDiGraph) -> List[Tuple]:
    """
    :param cfg: The context-free grammar
    :param graph: The graph
    :return: List of tuples (start_node, nonterminal, end_node)
    """
    weak_cnf = cfg_to_weak_cnf(cfg)
    term_prods = []
    nonterm_prods = []
    epsilons = []
    for prod in weak_cnf.productions:
        if len(prod.body) == 1:
            term_prods.append(prod)
        elif len(prod.body) == 2:
            nonterm_prods.append(prod)
        else:
            epsilons.append(prod)

    r = []
    edges = graph.edges(data="label")
    for (u, v, label) in edges:
        for prod in term_prods:
            if label == prod.body[0].to_text():
                r.append((u, prod.head.to_text(), v))
    for node in graph.nodes():
        for prod in epsilons:
            r.append((node, prod.head.to_text(), node))
    m = r.copy()
    while len(m) > 0:
        (u, N, v) = m.pop()

        for (a, NT, b) in r:
            if u == b:
                for prod in nonterm_prods:
                    if NT == prod.body[0].to_text() and N == prod.body[1].to_text():
                        if (a, prod.head.to_text(), v) not in r:
                            r.append((a, prod.head.to_text(), v))
                            m.append((a, prod.head.to_text(), v))

        for (a, NT, b) in r:
            if v == a:
                for prod in nonterm_prods:
                    if NT == prod.body[1].to_text() and N == prod.body[0].to_text():
                        if (u, prod.head.to_text(), b) not in r:
                            r.append((u, prod.head.to_text(), b))
                            m.append((u, prod.head.to_text(), b))
    return r


def cfpq(
    graph: MultiDiGraph,
    cfg: CFG,
    start: Set = None,
    finish: Set = None,
    start_nonterminal: Variable = Variable("S"),
) -> Set[Tuple]:
    """
    :param graph: The graph
    :param cfg: The context-free grammar
    :param start: The set of start vertices
    :param finish: The set of final vertices
    :return: Set of tuples (start_node, end_node). Pairs of vertices which are connected by a path, corresponding to a cfg
    """
    if start is None:
        start = set(graph.nodes())
    if finish is None:
        finish = set(graph.nodes())

    r = hellings(cfg, graph)
    result = set()
    for (u, N, v) in r:
        if u in start and v in finish and N == start_nonterminal:
            result.add((u, v))
    return result
