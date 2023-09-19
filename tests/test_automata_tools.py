import networkx as nx
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
)
from pyformlang.regular_expression import Regex

from project import finite_automata_tools
from project import graph_module


def test_empty_regex_to_automaton():
    empty_dfa = finite_automata_tools.regex_to_dfa(Regex(""))
    expected = DeterministicFiniteAutomaton()
    assert empty_dfa == expected


def test_empty_graph_to_automaton():
    expected = NondeterministicFiniteAutomaton()
    actual = nx.MultiDiGraph()
    assert expected == finite_automata_tools.graph_to_nfa(actual)


def test_regex_kleene_to_dfa():
    expected = DeterministicFiniteAutomaton()
    expected.add_start_state(1)
    expected.add_final_state(1)
    expected.add_transitions([(1, "a", 2), (2, "b", 1)])
    automaton = finite_automata_tools.regex_to_dfa(Regex("(a.b)*"))
    assert expected.is_equivalent_to(automaton)
    assert expected == automaton
    assert expected.minimize() == automaton


def test_regex_or_to_dfa():
    expected = DeterministicFiniteAutomaton()
    expected.add_start_state(1)
    expected.add_final_state(2)
    expected.add_transitions([(1, "a", 3), (3, "b", 2)])
    expected.add_transitions([(1, "c", 4), (4, "d", 2)])
    automaton = finite_automata_tools.regex_to_dfa(Regex("(a.b)|(c.d)"))
    assert expected.is_equivalent_to(automaton)
    assert expected == automaton
    assert expected.minimize() == automaton


def test_simple_graph_to_automaton():
    expected = NondeterministicFiniteAutomaton()
    expected.add_start_state(1)
    expected.add_final_state(2)
    expected.add_transitions([(1, "a", 2)])
    automaton = finite_automata_tools.graph_to_nfa(
        nx.MultiDiGraph([(1, 2, {"label": "a"})]), {1}, {2}
    )
    assert expected.is_equivalent_to(automaton)
    assert expected == automaton
    assert expected.minimize() == automaton


def test_synthetic_graph_to_nfa():
    expected = NondeterministicFiniteAutomaton()
    expected.add_start_state(0)
    expected.add_final_state(0)
    expected.add_transitions(
        [
            (1, "a", 2),
            (2, "a", 3),
            (3, "a", 0),
            (0, "a", 1),
            (4, "b", 5),
            (5, "b", 6),
            (6, "b", 0),
            (0, "b", 4),
        ]
    )
    automaton = finite_automata_tools.graph_to_nfa(
        graph_module.generate_two_cycles_graph(3, 3, ("a", "b")), {0}, {0}
    )
    assert expected.is_equivalent_to(automaton)
    assert expected == automaton


def test_downloaded_graph_to_nfa_metrics():
    nodes_num, edges_num, labels = graph_module.get_graph_metrics_by_name("travel")
    graph = graph_module.get_graph("travel")
    automaton = finite_automata_tools.graph_to_nfa(graph)
    assert nodes_num == len(automaton.states)
    assert labels == automaton.symbols
    assert edges_num == automaton.get_number_transitions()


def test_graph_without_labels_to_nfa():
    expected = NondeterministicFiniteAutomaton()
    graph = nx.MultiDiGraph([(1, 2), (2, 3), (3, 1)])
    expected.add_start_state(1)
    expected.add_final_state(1)
    expected.add_start_state(2)
    expected.add_final_state(2)
    expected.add_start_state(3)
    expected.add_final_state(3)
    automata = finite_automata_tools.graph_to_nfa(graph)
    assert expected == automata
    assert automata.get_number_transitions() == 0
    assert automata.final_states == {1, 2, 3}
    assert automata.start_states == {1, 2, 3}
