from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, Symbol, State
from pyformlang.regular_expression import Regex

from project.finite_automata_tools import regex_to_dfa
from project.rpq import fa_intersection, rpq


def test_fa_intersect():
    actual = NondeterministicFiniteAutomaton()
    actual.add_start_state(State(0))
    actual.add_final_state(State(1))
    actual.add_transitions(
        [
            (State(0), Symbol("a"), State(0)),
            (State(0), Symbol("a"), State(1)),
            (State(1), Symbol("c"), State(1)),
            (State(1), Symbol("b"), State(1)),
        ]
    )
    assert actual.accepts([Symbol("a"), Symbol("c")])
    actual2 = NondeterministicFiniteAutomaton()
    actual2.add_start_state(State(0))
    actual2.add_final_state(State(1))
    actual2.add_transitions(
        [
            (State(0), Symbol("a"), State(0)),
            (State(0), Symbol("b"), State(1)),
            (State(1), Symbol("c"), State(1)),
            (State(1), Symbol("b"), State(0)),
        ]
    )

    expected = NondeterministicFiniteAutomaton()
    expected.add_start_state(State(0))
    expected.add_final_state(State(2))
    expected.add_transitions(
        [
            (State(0), "a", State(0)),
            (State(0), "a", State(1)),
            (State(1), "b", State(2)),
            (State(2), "b", State(1)),
            (State(2), "c", State(2)),
        ]
    )
    intersection = fa_intersection(actual, actual2)
    assert expected == intersection
    assert intersection.is_equivalent_to(expected)
    assert actual.accepts([Symbol("a"), Symbol("c")])
    assert intersection.accepts([Symbol("a"), Symbol("b"), Symbol("c")])
    assert not intersection.accepts([Symbol("a"), Symbol("c")])


def test_automata_intersection1():
    automaton1 = regex_to_dfa(Regex("a.(b|c)*.d"))
    automaton2 = regex_to_dfa(Regex("a.(c|d)*.d"))
    intersection = fa_intersection(automaton1, automaton2)
    assert not intersection.accepts(
        [Symbol("a"), Symbol("b"), Symbol("c"), Symbol("d")]
    )
    assert not intersection.accepts(
        [Symbol("a"), Symbol("d"), Symbol("c"), Symbol("d")]
    )
    assert intersection.accepts([Symbol("a"), Symbol("c"), Symbol("c"), Symbol("d")])
    assert not intersection.accepts([Symbol("a"), Symbol("d"), Symbol("d")])


def test_automata_intersection2():
    automaton1 = regex_to_dfa(Regex("(a|b).c.(a|b)"))
    automaton2 = regex_to_dfa(Regex("(a|b).(c|d).(a|b)"))
    intersection = fa_intersection(automaton1, automaton2)
    assert not intersection.accepts([Symbol("a"), Symbol("c")])
    assert not intersection.accepts([Symbol("b"), Symbol("d")])
    assert intersection.accepts([Symbol("a"), Symbol("c"), Symbol("a")])
    assert intersection.accepts([Symbol("b"), Symbol("c"), Symbol("b")])


def test_rpq1():
    automaton = NondeterministicFiniteAutomaton()
    automaton.add_transition(State(0), Symbol("a"), State(1))
    automaton.add_transition(State(1), Symbol("b"), State(2))
    automaton.add_transition(State(2), Symbol("c"), State(3))
    automaton.add_transition(State(3), Symbol("d"), State(4))
    automaton.add_transition(State(0), Symbol("a"), State(5))
    automaton.add_transition(State(5), Symbol("e"), State(6))
    graph = automaton.to_networkx()
    assert rpq(graph, Regex("(a|f).(b|d)*.c"), {0}, {3}) == {(0, 3)}


def test_rpq2():
    automaton = NondeterministicFiniteAutomaton()
    automaton.add_transition(State(0), Symbol("a"), State(1))
    automaton.add_transition(State(1), Symbol("b"), State(2))
    automaton.add_transition(State(2), Symbol("c"), State(3))
    automaton.add_transition(State(0), Symbol("a"), State(4))
    automaton.add_transition(State(4), Symbol("d"), State(5))
    graph = automaton.to_networkx()
    assert rpq(graph, Regex("(a.b.c)|(a.d)"), {0}, {3, 5}) == {(0, 3), (0, 5)}


def test_rpq3():
    automaton = NondeterministicFiniteAutomaton()
    automaton.add_transition(State(0), Symbol("a"), State(1))
    automaton.add_transition(State(1), Symbol("b"), State(2))
    automaton.add_transition(State(2), Symbol("c"), State(3))
    automaton.add_transition(State(3), Symbol("d"), State(4))
    automaton.add_transition(State(4), Symbol("e"), State(5))
    graph = automaton.to_networkx()
    assert rpq(
        graph, Regex("(a.b.c.d.e)|(a.b.c.d)|(a.b.c)|(a.b)|(a)"), {0}, {5, 4, 3, 2, 1}
    ) == {(0, 5), (0, 4), (0, 3), (0, 2), (0, 1)}
