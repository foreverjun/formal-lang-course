from networkx import MultiDiGraph
from pyformlang.finite_automaton import (
    State,
)
from pyformlang.regular_expression import Regex
from scipy.sparse import lil_matrix, csr_matrix, vstack, block_diag

from project.finite_automata_tools import graph_to_nfa, regex_to_dfa
from project.rpq import decompose_automaton, FABooleanDecomposition


def create_bfs_front(
    graph_automation: FABooleanDecomposition,
    regex_automation: FABooleanDecomposition,
    start_indexes: set,
):
    buf_matrix = lil_matrix(
        (
            len(regex_automation.states_to_index),
            len(graph_automation.states_to_index)
            + len(regex_automation.states_to_index),
        ),
        dtype=bool,
    )
    row = lil_matrix((1, len(graph_automation.states_to_index)), dtype=bool)
    for i in start_indexes:
        row[0, i] = True
    for i in regex_automation.start_states:
        buf_matrix[
            regex_automation.states_to_index[i], regex_automation.states_to_index[i]
        ] = True
        buf_matrix[
            regex_automation.states_to_index[i], len(regex_automation.states_to_index) :
        ] = row
    return buf_matrix.tocsr()


def normalize_front(regex_bin_dec: FABooleanDecomposition, front: csr_matrix):
    res = lil_matrix(front.shape, dtype=bool)
    for i, j in zip(*front.nonzero()):
        if front[
            i, len(regex_bin_dec.states_to_index) :
        ].count_nonzero() > 0 and j < len(regex_bin_dec.states_to_index):
            node_number = i // len(regex_bin_dec.states_to_index)
            res[node_number * len(regex_bin_dec.states_to_index) + j, j] = True
            res[
                node_number * len(regex_bin_dec.states_to_index) + j,
                len(regex_bin_dec.states_to_index) :,
            ] += front[i, len(regex_bin_dec.states_to_index) :]
    return res.tocsr()


def bfs_rpq(
    graph: MultiDiGraph,
    regex: Regex,
    start_nodes: set = None,
    final_nodes: set = None,
    for_each_node: bool = False,
):
    graph_bool_dec = decompose_automaton(graph_to_nfa(graph, start_nodes, final_nodes))
    regex_bool_dec = decompose_automaton(regex_to_dfa(regex))
    print(len(regex_bool_dec.states_to_index))
    print(regex_bool_dec.states_to_index)
    print(regex_bool_dec.final_states)
    print(regex_bool_dec.start_states)
    print(graph_bool_dec.states_to_index)

    start_indexes = {
        graph_bool_dec.states_to_index[st] for st in graph_bool_dec.start_states
    }
    # Create bfs front
    front = (
        vstack(
            [
                create_bfs_front(
                    graph_bool_dec, regex_bool_dec, {graph_bool_dec.states_to_index[st]}
                )
                for st in graph_bool_dec.start_states
            ]
        )
        if for_each_node
        else create_bfs_front(graph_bool_dec, regex_bool_dec, start_indexes)
    )

    matrix_direct_sums = {}

    for label in (
        regex_bool_dec.decomposition.keys() & graph_bool_dec.decomposition.keys()
    ):
        matrix_direct_sums[label] = block_diag(
            (regex_bool_dec.decomposition[label], graph_bool_dec.decomposition[label])
        )

    visited = csr_matrix(front.shape, dtype=bool)
    is_first = True

    while True:
        prev = visited.count_nonzero()

        for dec_matrix in matrix_direct_sums.values():
            if is_first:
                renewed_front = front @ dec_matrix
            else:
                renewed_front = visited @ dec_matrix
            visited += normalize_front(regex_bool_dec, renewed_front)
        is_first = False

        if prev == visited.count_nonzero():
            break

    res = set()
    graph_index_to_state = {v: k for k, v in graph_bool_dec.states_to_index.items()}
    regex_index_to_state = {v: k for k, v in regex_bool_dec.states_to_index.items()}
    print(len(regex_bool_dec.states_to_index))
    print(regex_bool_dec.final_states)
    for i, j in zip(*visited.nonzero()):
        if len(graph_bool_dec.states_to_index) <= j:
            print(len(graph_bool_dec.states_to_index) <= j)
            print(
                graph_index_to_state[j - len(regex_bool_dec.states_to_index)]
                in graph_bool_dec.final_states
            )
            print(
                regex_index_to_state[i % len(regex_bool_dec.states_to_index)]
                in regex_bool_dec.final_states
            )
            print(i, j)
            print(regex_index_to_state[i % len(regex_bool_dec.states_to_index)])
        if (
            len(regex_bool_dec.states_to_index) <= +j
            and graph_index_to_state[j - len(regex_bool_dec.states_to_index)]
            in graph_bool_dec.final_states
            and regex_index_to_state[i % len(regex_bool_dec.states_to_index)]
            in regex_bool_dec.final_states
        ):
            state_index = j - len(regex_bool_dec.states_to_index)
            if graph_index_to_state[state_index] in graph_bool_dec.final_states:
                if for_each_node:
                    res.add(
                        (
                            State(i // len(regex_bool_dec.states_to_index)),
                            State(state_index),
                        )
                    )
                else:
                    res.add(State(state_index))

    return res
