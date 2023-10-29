from pyformlang.cfg import CFG, Variable, Terminal, Production
from pyformlang.finite_automaton import EpsilonNFA
from typing import Dict, Set
from pyformlang.regular_expression import Regex


class RSM:
    def __init__(self, start_v: Variable, automations: Dict[Variable, EpsilonNFA]):
        self.start_v = start_v
        self.automations = automations


class ECFG:
    def __init__(
        self,
        variables: Set[Variable],
        start_v: Variable,
        productions: Dict[Variable, Regex],
        terminals: Set[Terminal] = None,
    ):
        self.variables = variables
        self.terminals = terminals
        self.start_v = start_v
        self.productions = productions


def ecfg_from_text(text: str, start_v=Variable("S")) -> ECFG:
    lines = text.strip().split("\n")
    variables = set()
    productions = dict()
    for line in lines:
        if line.strip() == "":
            continue
        prod = line.split("->")
        var, body = prod[0].strip(), prod[1].strip()
        variables.add(Variable(var))
        productions[Variable(var)] = Regex(body)
    return ECFG(variables, start_v, productions)


def ecfg_from_file(file_name: str, start_v: Variable = Variable("S")) -> ECFG:
    with open(file_name, "r") as file:
        return ecfg_from_text(file.read(), start_v)


def cfg_to_ecfg(cfg: CFG) -> ECFG:
    productions = {}
    for prod in cfg.productions:
        regex_text = " "
        if len(prod.body) == 0:
            regex_text = "$"
        for symb in prod.body:
            if symb.to_text().strip() == "":
                continue
            regex_text += symb.to_text().strip() + " "
        regex_text = regex_text.strip()
        if prod.head not in productions:
            productions[prod.head] = Regex(regex_text)
        else:
            productions[prod.head] = productions[prod.head].union(Regex(regex_text))
    return ECFG(set(cfg.variables), cfg.start_symbol, productions, set(cfg.terminals))


def ecfg_to_rsm(ecfg: ECFG) -> RSM:
    automations = {}
    for var in ecfg.variables:
        automations[var] = ecfg.productions[var].to_epsilon_nfa()
    return RSM(ecfg.start_v, automations)


def minimize_rsm(rsm: RSM) -> RSM:
    for var in rsm.automations:
        rsm.automations[var] = rsm.automations[var].minimize()
    return rsm
