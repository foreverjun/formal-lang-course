import os

from project.task_6 import cfg_from_file
from project.task_7 import *
from project.finite_automata_tools import regex_to_dfa


def test_ecfg_from_file():
    expected = ECFG({Variable("S")}, Variable("S"), {Variable("S"): Regex("a.S.b")})
    current_dir_path = os.path.dirname(os.path.realpath(__file__))
    actual = ecfg_from_file(os.path.join(current_dir_path, "res", "ecfg_1"))
    assert actual.start_v == expected.start_v
    assert actual.variables == expected.variables
    for v in actual.variables:
        assert (
            actual.productions[v]
            .to_epsilon_nfa()
            .is_equivalent_to(expected.productions[v].to_epsilon_nfa())
        )


def test_ecfg_from_file_2():
    expected = ECFG(
        {Variable("S"), Variable("A"), Variable("C"), Variable("B")},
        Variable("S"),
        {
            Variable("S"): Regex("(A.B)|(B.C)"),
            Variable("A"): Regex("(a.A)|a"),
            Variable("B"): Regex("(b.B)|b"),
            Variable("C"): Regex("(c.C)|c"),
        },
    )
    current_dir_path = os.path.dirname(os.path.realpath(__file__))
    actual = ecfg_from_file(os.path.join(current_dir_path, "res", "cfg_2"))
    assert actual.start_v == expected.start_v
    assert actual.variables == expected.variables
    for v in actual.variables:
        assert (
            actual.productions[v]
            .to_epsilon_nfa()
            .is_equivalent_to(expected.productions[v].to_epsilon_nfa())
        )


def test_ecfg_from_cfg():
    current_dir_path = os.path.dirname(os.path.realpath(__file__))
    cfg = cfg_from_file(os.path.join(current_dir_path, "res", "cfg_1"), "S")
    ecfg = cfg_to_ecfg(cfg)
    expected = ECFG({Variable("S")}, Variable("S"), {Variable("S"): Regex("a.S.b|a.b")})
    assert ecfg.start_v == expected.start_v
    assert ecfg.variables == expected.variables
    for v in ecfg.variables:
        assert (
            ecfg.productions[v]
            .to_epsilon_nfa()
            .is_equivalent_to(expected.productions[v].to_epsilon_nfa())
        )


def test_ecfg_from_cfg_2():
    current_dir_path = os.path.dirname(os.path.realpath(__file__))
    cfg = cfg_from_file(os.path.join(current_dir_path, "res", "cfg_2"), "S")
    ecfg = cfg_to_ecfg(cfg)
    expected = ECFG(
        {Variable("S"), Variable("A"), Variable("C"), Variable("B")},
        Variable("S"),
        {
            Variable("S"): Regex("(A.B)|(B.C)"),
            Variable("A"): Regex("(a.A)|a"),
            Variable("B"): Regex("(b.B)|b"),
            Variable("C"): Regex("(c.C)|c"),
        },
    )
    assert ecfg.start_v == expected.start_v
    assert ecfg.variables == expected.variables
    for v in ecfg.variables:
        assert (
            ecfg.productions[v]
            .to_epsilon_nfa()
            .is_equivalent_to(expected.productions[v].to_epsilon_nfa())
        )


def test_rsm_from_ecfg():
    current_dir_path = os.path.dirname(os.path.realpath(__file__))
    ecfg = ecfg_from_file(os.path.join(current_dir_path, "res", "ecfg_1"))
    rsm = ecfg_to_rsm(ecfg)
    assert rsm.start_v == ecfg.start_v
    for v in rsm.automations:
        assert rsm.automations[v].is_equivalent_to(ecfg.productions[v].to_epsilon_nfa())


def test_rsm_from_ecfg_2():
    current_dir_path = os.path.dirname(os.path.realpath(__file__))
    ecfg = ecfg_from_file(os.path.join(current_dir_path, "res", "cfg_2"))
    rsm = ecfg_to_rsm(ecfg)
    assert rsm.start_v == ecfg.start_v
    for v in rsm.automations:
        assert rsm.automations[v].is_equivalent_to(ecfg.productions[v].to_epsilon_nfa())


def test_rsm_from_ecfg_3():
    text = """
    S -> a.A.b|a.b
    A -> a.A.B|$
    B -> b.B|$
    """
    ecfg = ecfg_from_text(text, "S")
    rsm = ecfg_to_rsm(ecfg)
    expected = RSM(
        Variable("S"),
        {
            Variable("S"): Regex("a.A.b|a.b").to_epsilon_nfa(),
            Variable("A"): Regex("a.A.B|$").to_epsilon_nfa(),
            Variable("B"): Regex("b.B|$").to_epsilon_nfa(),
        },
    )
    assert rsm.start_v == expected.start_v
    for v in rsm.automations:
        assert rsm.automations[v].is_equivalent_to(expected.automations[v])


def test_minimize_rsm():
    text = """
    S -> A B C
    A -> a
    B -> b
    C -> (a | S)
    """
    ecfg = ecfg_from_text(text, "S")
    rsm = ecfg_to_rsm(ecfg)
    rsm = minimize_rsm(rsm)
    for v in rsm.automations:
        assert rsm.automations[v].is_equivalent_to(regex_to_dfa(ecfg.productions[v]))
