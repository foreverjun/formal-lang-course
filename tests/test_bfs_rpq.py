from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, Symbol, State
from pyformlang.regular_expression import Regex

from project.bfs_rpq import bfs_rpq


def test_1():
    automaton = NondeterministicFiniteAutomaton()
    automaton.add_transition(State(0), Symbol("a"), State(1))
    automaton.add_transition(State(1), Symbol("b"), State(2))
    automaton.add_transition(State(2), Symbol("a"), State(3))
    automaton.add_transition(State(3), Symbol("b"), State(4))
    automaton.add_transition(State(0), Symbol("b"), State(5))
    automaton.add_transition(State(5), Symbol("a"), State(6))
    automaton.add_transition(State(6), Symbol("b"), State(7))
    graph = automaton.to_networkx()
    assert bfs_rpq(graph, Regex("(a|b).(a|b)"), {0}) == {2, 6}


def test_2():
    automaton = NondeterministicFiniteAutomaton()
    automaton.add_transition(State(0), Symbol("p"), State(1))
    automaton.add_transition(State(1), Symbol("q"), State(2))
    automaton.add_transition(State(2), Symbol("r"), State(3))
    automaton.add_transition(State(0), Symbol("r"), State(4))
    automaton.add_transition(State(4), Symbol("q"), State(5))
    graph = automaton.to_networkx()
    assert bfs_rpq(graph, Regex("(p|r).(q*)"), {0}, {1, 4, 5}) == {1, 4, 5}


def test_3():
    automaton = NondeterministicFiniteAutomaton()
    automaton.add_transition(State(0), Symbol("s"), State(1))
    automaton.add_transition(State(1), Symbol("t"), State(2))
    automaton.add_transition(State(2), Symbol("u"), State(3))
    graph = automaton.to_networkx()
    assert bfs_rpq(graph, Regex("(s|t).(u*)"), {0}, {1}) == {1}


def test_4():
    automaton = NondeterministicFiniteAutomaton()
    automaton.add_transition(State(0), Symbol("w"), State(1))
    automaton.add_transition(State(1), Symbol("x"), State(2))
    automaton.add_transition(State(2), Symbol("y"), State(3))
    automaton.add_transition(State(3), Symbol("z"), State(4))
    graph = automaton.to_networkx()
    assert bfs_rpq(graph, Regex("(w|x)*.(x*).(z*)"), {0}, for_each_node=True) == {
        (0, 1),
        (0, 2),
    }


def test_5():
    automaton = NondeterministicFiniteAutomaton()
    automaton.add_transition(State(4), Symbol("k"), State(5))
    automaton.add_transition(State(4), Symbol("c"), State(7))
    automaton.add_transition(State(4), Symbol("n"), State(6))
    automaton.add_transition(State(5), Symbol("e"), State(6))
    automaton.add_transition(State(7), Symbol("e"), State(6))
    automaton.add_transition(State(0), Symbol("k"), State(1))
    automaton.add_transition(State(1), Symbol("k"), State(2))
    automaton.add_transition(State(1), Symbol("n"), State(3))
    automaton.add_transition(State(2), Symbol("n"), State(3))
    automaton.add_transition(State(3), Symbol("c"), State(4))
    graph = automaton.to_networkx()
    assert bfs_rpq(graph, Regex("(k*).(n*).(c*).(e*)"), {0, 4}, for_each_node=True) == {
        (0, 1),
        (0, 7),
        (0, 4),
        (1, 5),
        (0, 3),
        (0, 6),
        (0, 2),
        (1, 7),
        (1, 6),
    }
