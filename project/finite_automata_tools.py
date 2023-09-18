from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from pyformlang.regular_expression import Regex


def regex_to_finite_minimal_automata(regex: Regex) -> DeterministicFiniteAutomaton:
    """
    Converts a regular expression to a minimal finite automata.
    :param regex: The regular expression to convert.
    :return: The minimal finite automata.
    """
    return regex.to_epsilon_nfa().minimize()
