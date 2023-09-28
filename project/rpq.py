from dataclasses import dataclass, field
from typing import Tuple, Any

import networkx as nx
from pyformlang.finite_automaton import (
    FiniteAutomaton,
    State,
    NondeterministicFiniteAutomaton,
)
from pyformlang.regular_expression import Regex
from scipy.sparse import csr_matrix, kron

from project.finite_automata_tools import graph_to_nfa, regex_to_dfa


@dataclass
class FABooleanDecomposition:
    start_states: set[Any] = field(default_factory=set)
    final_states: set[Any] = field(default_factory=set)
    states_to_index: dict[Any, int] = field(default_factory=dict)
    decomposition: dict[Any, csr_matrix] = field(default_factory=dict)


def decompose_automaton(automaton: FiniteAutomaton) -> FABooleanDecomposition:
    """
    Decompose a finite automaton into a set of boolean matrices.
    :param automaton: The automaton to decompose.
    :return: The bool_decomposition.
    """
    automaton = automaton.copy()
    bool_decomposition = FABooleanDecomposition()
    bool_decomposition.start_states = automaton.start_states.copy()
    bool_decomposition.final_states = automaton.final_states.copy()
    for state in bool_decomposition.start_states:
        automaton.remove_start_state(State(state))
    for state in bool_decomposition.final_states:
        automaton.remove_final_state(State(state))
    graph = automaton.to_networkx()
    edges = graph.edges(data="label")
    nodes = graph.nodes()
    counter = 0
    for node in nodes:
        bool_decomposition.states_to_index[node] = counter
        counter += 1

    decomposition_buf: dict[str : Tuple[list[int], list[int], list[int]]] = {}
    for edge in edges:
        if edge[2] is not None:
            if edge[2] not in decomposition_buf:
                decomposition_buf[edge[2]] = (list(), list(), list())
            decomposition_buf[edge[2]][0].append(
                bool_decomposition.states_to_index[edge[0]]
            )
            decomposition_buf[edge[2]][1].append(
                bool_decomposition.states_to_index[edge[1]]
            )
            decomposition_buf[edge[2]][2].append(1)

    for key in decomposition_buf:
        bool_decomposition.decomposition[key] = csr_matrix(
            (
                decomposition_buf[key][2],
                (decomposition_buf[key][0], decomposition_buf[key][1]),
            ),
            shape=(len(nodes), len(nodes)),
        )
    return bool_decomposition


def decomposition_intersection(
    first_decomposition: FABooleanDecomposition,
    second_decomposition: FABooleanDecomposition,
) -> FABooleanDecomposition:
    result_decomposition = dict()
    for label in (
        first_decomposition.decomposition.keys()
        & second_decomposition.decomposition.keys()
    ):
        result_decomposition[label] = kron(
            first_decomposition.decomposition[label],
            second_decomposition.decomposition[label],
        )

    result_state_to_index = dict()
    second_dimension = len(second_decomposition.states_to_index)
    for f_key in first_decomposition.states_to_index:
        for s_key in second_decomposition.states_to_index:
            result_state_to_index[(f_key, s_key)] = (
                first_decomposition.states_to_index[f_key] * second_dimension
                + second_decomposition.states_to_index[s_key]
            )

    result_start_states = set()
    for f_start in first_decomposition.start_states:
        for s_start in second_decomposition.start_states:
            result_start_states.add((f_start, s_start))

    result_final_states = set()
    for f_final in first_decomposition.final_states:
        for s_final in second_decomposition.final_states:
            result_final_states.add((f_final, s_final))

    return FABooleanDecomposition(
        result_start_states,
        result_final_states,
        result_state_to_index,
        result_decomposition,
    )


def fa_intersection(
    first_automation: FiniteAutomaton, second_automation: FiniteAutomaton
) -> FiniteAutomaton():
    first_fa_decomposition = decompose_automaton(first_automation)
    second_fa_decomposition = decompose_automaton(second_automation)
    intersection_decomposition = decomposition_intersection(
        first_fa_decomposition, second_fa_decomposition
    )
    index_to_state = {
        v: k for k, v in intersection_decomposition.states_to_index.items()
    }
    # transfer decomposition to FiniteAutomaton
    automation = NondeterministicFiniteAutomaton()
    for label, matrix in intersection_decomposition.decomposition.items():
        matrix.eliminate_zeros()
        for i in range(matrix.todense().shape[0]):
            for j in range(matrix.todense().shape[1]):
                if matrix.todense()[i, j] == 1:
                    automation.add_transition(
                        State(index_to_state[i]), label, State(index_to_state[j])
                    )
    for state in intersection_decomposition.start_states:
        automation.add_start_state(State(state))

    for state in intersection_decomposition.final_states:
        automation.add_final_state(State(state))

    return automation


def transitive_closure(matrix: csr_matrix) -> list[tuple[int, int]]:
    if not matrix.nnz:
        return []

    matrix.eliminate_zeros()

    prev = -1
    curr = matrix.nnz
    while prev != curr:
        matrix += matrix @ matrix
        prev = curr
        curr = matrix.nnz

    return list(zip(*matrix.nonzero()))


def rpq(
    graph: nx.MultiDiGraph,
    regex: Regex,
    start_states: set[int] = None,
    final_states: set[int] = None,
) -> set[tuple[int, int]]:
    gr_automation = graph_to_nfa(graph, start_states, final_states)
    re_automation = regex_to_dfa(regex)
    intersection = decomposition_intersection(
        decompose_automaton(gr_automation), decompose_automaton(re_automation)
    )
    index_to_state = {v: k for k, v in intersection.states_to_index.items()}
    n = len(intersection.states_to_index)
    sum_matrix = sum(intersection.decomposition.values(), start=csr_matrix((n, n)))
    closure_pairs = transitive_closure(sum_matrix)
    result = set()
    # states to indexes
    start_indexes = {
        intersection.states_to_index[state] for state in intersection.start_states
    }
    finish_indexes = {
        intersection.states_to_index[state] for state in intersection.final_states
    }
    for start, finish in closure_pairs:
        if start in start_indexes and finish in finish_indexes:
            result.add((index_to_state[start][0], index_to_state[finish][0]))
    return result
