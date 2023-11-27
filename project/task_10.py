from typing import Set, Tuple

from networkx import MultiDiGraph
from pyformlang.cfg import CFG, Variable
from pyformlang.finite_automaton import EpsilonNFA, State
from scipy.sparse import eye, csr_matrix

from project.rpq import (
    decompose_automaton,
    decomposition_intersection,
    transitive_closure,
)
from project.task_7 import cfg_to_ecfg, ecfg_to_rsm, minimize_rsm


def cfpq_tensors(
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

    r = tensors_algo(cfg, graph)
    result = set()
    for (u, N, v) in r:
        if u in start and v in finish and N == start_nonterminal.value:
            result.add((u, v))
    return result


def cfg_to_automation(cfg: CFG) -> EpsilonNFA:
    rsm = ecfg_to_rsm(cfg_to_ecfg(cfg))
    rsm = minimize_rsm(rsm)
    automation = EpsilonNFA()
    for nonterm, aut in rsm.automations.items():
        for start in aut.start_states:
            automation.add_start_state(State((nonterm.value, start)))
        for final in aut.final_states:
            automation.add_final_state(State((nonterm.value, final)))
        for st, label, fin in aut:
            automation.add_transition(
                State((nonterm.value, st)), label, State((nonterm.value, fin))
            )
    return automation


def tensors_algo(cfg: CFG, graph: MultiDiGraph) -> Set[Tuple]:
    """
    :param cfg: The context-free grammar
    :param graph: The graph
    :return: Set of tuples (start_node, nonterminal, end_node). Pairs of vertices which are connected by a path, corresponding to a cfg
    """
    cfg_decomposition = decompose_automaton(cfg_to_automation(cfg))
    # add paths for epsilons
    nullable = cfg.get_nullable_symbols()
    for nonterm in nullable:
        n = len(cfg_decomposition.states_to_index)
        if nonterm in cfg_decomposition.decomposition:
            cfg_decomposition.decomposition[nonterm] += eye(n, n, dtype=bool)
        else:
            cfg_decomposition.decomposition[nonterm] += eye(n, n, dtype=bool)

    graph_decomposition = decompose_automaton(
        EpsilonNFA.from_networkx(graph).remove_epsilon_transitions()
    )
    # index to states
    cfg_index_to_state = {v: k for k, v in cfg_decomposition.states_to_index.items()}
    graph_index_to_state = {
        v: k for k, v in graph_decomposition.states_to_index.items()
    }
    closure_nnz = -1
    is_continue = True
    while is_continue:
        intersection = decomposition_intersection(
            cfg_decomposition, graph_decomposition
        )
        sum_matrix = sum(intersection.decomposition.values())
        closure_pairs = transitive_closure(sum_matrix)
        if closure_nnz == len(closure_pairs):
            is_continue = False
        closure_nnz = len(closure_pairs)
        for start, finish in closure_pairs:
            n = len(graph_decomposition.states_to_index)
            cfg_i = start // n
            cfg_j = finish // n
            graph_i = start % n
            graph_j = finish % n
            var = cfg_index_to_state[cfg_i][0]
            if (
                cfg_index_to_state[cfg_i] in cfg_decomposition.start_states
                and cfg_index_to_state[cfg_j] in cfg_decomposition.final_states
            ):
                if var not in graph_decomposition.decomposition:
                    graph_decomposition.decomposition[var] = csr_matrix(
                        (
                            len(graph_decomposition.states_to_index),
                            len(graph_decomposition.states_to_index),
                        ),
                        dtype=bool,
                    )
                graph_decomposition.decomposition[var][graph_i, graph_j] = True
    result = set()
    for var, matrix in graph_decomposition.decomposition.items():
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                if matrix[i, j]:
                    result.add((graph_index_to_state[i], var, graph_index_to_state[j]))

    return result
