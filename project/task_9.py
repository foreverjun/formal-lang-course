from typing import Set, Tuple

from networkx import MultiDiGraph
from pyformlang.cfg import CFG, Variable
from scipy.sparse import dok_matrix

from project.task_6 import cfg_to_weak_cnf


def matrices_algo(cfg: CFG, graph: MultiDiGraph) -> Set[Tuple]:
    """
    :param cfg: The context-free grammar
    :param graph: The graph
    :return: Set of tuples (start_node, end_node)
    """
    weak_cnf = cfg_to_weak_cnf(cfg)
    term_prods = set()
    nonterm_prods = set()
    epsilons = set()
    for prod in weak_cnf.productions:
        if len(prod.body) == 1:
            term_prods.add(prod)
        elif len(prod.body) == 2:
            nonterm_prods.add(prod)
        else:
            epsilons.add(prod)
    nodes_num = graph.number_of_nodes()
    nonterm_to_matrix = {}
    for variable in weak_cnf.variables:
        nonterm_to_matrix[variable.value] = dok_matrix(
            (nodes_num, nodes_num), dtype=bool
        )
    for node in graph.nodes:
        for prod in epsilons:
            nonterm_to_matrix[prod.head.value][node, node] = True

    for (u, v, label) in graph.edges(data="label"):
        for prod in term_prods:
            if prod.body[0].value == label:
                nonterm_to_matrix[prod.head.value][u, v] = True

    changed = True

    while changed:
        changed = False
        for prod in nonterm_prods:
            prevnnz = nonterm_to_matrix[prod.head.value].count_nonzero()
            nonterm_to_matrix[prod.head.value] += (
                nonterm_to_matrix[prod.body[0].value]
                @ nonterm_to_matrix[prod.body[1].value]
            )
            if nonterm_to_matrix[prod.head.value].count_nonzero() != prevnnz:
                changed = True

    res = set()

    for (nont, matrix) in nonterm_to_matrix.items():
        for elem in zip(*matrix.nonzero()):
            res.add((elem[0], nont, elem[1]))
    return res


def cfpq_matrices(
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

    r = matrices_algo(cfg, graph)
    result = set()
    for (u, N, v) in r:
        if u in start and v in finish and N == start_nonterminal.value:
            result.add((u, v))
    return result
