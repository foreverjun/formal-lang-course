from typing import Set

import networkx as nx
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
    EpsilonNFA,
)
from pyformlang.regular_expression import Regex


def regex_to_dfa(regex: Regex) -> DeterministicFiniteAutomaton:
    """
    Converts a regular expression to a minimal finite automata.
    :param regex: The regular expression to convert.
    :return: The minimal finite automata.
    """
    return regex.to_epsilon_nfa().minimize()


def graph_to_nfa(
    graph: nx.MultiDiGraph, start_states: Set[int] = None, final_states: Set[int] = None
) -> NondeterministicFiniteAutomaton:
    """
    Convert a networkx MultiDiGraph to a NondeterministicFiniteAutomaton
    :param start_states: The start states of the graph. If None, all nodes would be considered as start states.
    :param final_states: The final states of the graph. If None, all nodes would be considered as final states.
    :param graph: The graph to convert. Transitions must be labeled with strings. Transitions with no label would be ignored.
    Start and final states must be passed using start_states and final_states parameters. Keys of the graph nodes would not be used for this purpose.
    :return: The NondeterministicFiniteAutomaton
    """
    # Set start and final states of graph to false

    for node in graph.nodes(data="is_start"):
        graph.nodes[node[0]]["is_start"] = False
    for node in graph.nodes(data="is_final"):
        graph.nodes[node[0]]["is_final"] = False

    # Set start and final states of graph to true if they are in start_states or final_states.
    # If start_states or final_states is None, all nodes would be considered as start or final states respectively.

    if start_states is not None and start_states != set():
        for node in start_states:
            graph.nodes[node]["is_start"] = True
    else:
        for node in graph.nodes:
            if node in graph.nodes:
                graph.nodes[node]["is_start"] = True

    if final_states is not None and final_states != set():
        for node in final_states:
            if node in graph.nodes:
                graph.nodes[node]["is_final"] = True
    else:
        for node in graph.nodes:
            graph.nodes[node]["is_final"] = True

    # Return NFA

    return EpsilonNFA().from_networkx(graph).remove_epsilon_transitions()
