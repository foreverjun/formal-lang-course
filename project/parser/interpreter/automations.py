from abc import abstractmethod, ABC
from copy import copy
from pathlib import Path

import networkx as nx
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton as Nfa
from pyformlang.regular_expression import Regex
from pyformlang.cfg import CFG
from scipy.sparse import csr_matrix

from project.finite_automata_tools import regex_to_dfa, graph_to_nfa
from project.graph_module import get_graph
from project.parser.interpreter.set import Set
from project.parser.interpreter.tuples import Pair, Triple
from project.rpq import transitive_closure, decompose_automaton, fa_intersection
from project.task_7 import ecfg_to_rsm, cfg_to_ecfg
from project.task_6 import cfg_from_file


class AutomationAbstract:
    @property
    @abstractmethod
    def type(self):
        pass

    @abstractmethod
    def from_str(self, s) -> "AutomationAbstract":
        pass

    @abstractmethod
    def from_file(self, path: Path) -> "AutomationAbstract":
        pass

    @abstractmethod
    def set_start(self, start: "Set") -> "AutomationAbstract":
        pass

    @abstractmethod
    def set_final(self, final: "Set") -> "AutomationAbstract":
        pass

    @abstractmethod
    def add_start(self, start: "Set") -> "AutomationAbstract":
        pass

    @abstractmethod
    def add_final(self, final: "Set") -> "AutomationAbstract":
        pass

    @abstractmethod
    def get_start(self) -> "Set":
        pass

    @abstractmethod
    def get_final(self) -> "Set":
        pass

    @abstractmethod
    def get_labels(self) -> "Set":
        pass

    @abstractmethod
    def get_edges(self) -> "Set":
        pass

    @abstractmethod
    def get_nodes(self) -> "Set":
        pass

    @abstractmethod
    def get_reachable(self) -> "Set":
        pass

    @abstractmethod
    def intersect(self, other: "AutomationAbstract") -> "AutomationAbstract":
        pass

    @abstractmethod
    def union(self, other: "AutomationAbstract") -> "AutomationAbstract":
        pass

    @abstractmethod
    def concat(self, other: "AutomationAbstract") -> "AutomationAbstract":
        pass


class Automation(AutomationAbstract, ABC):
    def __init__(self, nfa: Nfa, ty=None):
        self._nfa = nfa
        states = Set({state.value for state in nfa.states}, ty)
        self._type = states.type

    @classmethod
    def from_str(cls, s: str) -> "Automation":
        return cls(regex_to_dfa(Regex(s)))

    @classmethod
    def from_file(cls, path: Path) -> "Automation":
        with open(path, "r") as f:
            graph = nx.nx_pydot.read_dot(f)
            return cls(graph_to_nfa(graph))

    @classmethod
    def load(cls, name: str) -> "Automation":
        return cls(graph_to_nfa(get_graph(name)))

    def set_start(self, start: "Set") -> "Automation":
        if isinstance(None, start.type):
            start = Set({state.value for state in self._nfa.states})
        if self._type != start.type:
            raise TypeError(
                "Expected set of type " + str(self._type) + ", got " + str(start.type)
            )
        return Automation(
            Nfa(
                states=copy(self._nfa.states),
                input_symbols=copy(self._nfa.symbols),
                start_state=start.elements,
                final_states=copy(self._nfa.final_states),
            )
        )

    def set_final(self, final: "Set") -> "Automation":
        if isinstance(None, final.type):
            final = Set({state.value for state in self._nfa.states})
        if self._type != final.type:
            raise TypeError(
                "Expected set of type " + str(self._type) + ", got " + str(final.type)
            )
        return Automation(
            Nfa(
                states=copy(self._nfa.states),
                input_symbols=copy(self._nfa.symbols),
                start_state=copy(self._nfa.start_states),
                final_states=final.elements,
            )
        )

    def add_start(self, start: "Set") -> "Automation":
        if isinstance(None, start.type):
            start = Set({state.value for state in self._nfa.states})
        if self._type != start.type:
            raise TypeError(
                "Expected set of type " + str(self._type) + ", got " + str(start.type)
            )
        return Automation(
            Nfa(
                states=copy(self._nfa.states),
                input_symbols=copy(self._nfa.symbols),
                start_state=copy(self._nfa.start_states).union(start.elements),
                final_states=copy(self._nfa.final_states),
            )
        )

    def add_final(self, final: "Set") -> "Automation":
        if isinstance(None, final.type):
            final = Set({state.value for state in self._nfa.states})
        if self._type != final.type:
            raise TypeError(
                "Expected set of type " + str(self._type) + ", got " + str(final.type)
            )
        return Automation(
            Nfa(
                states=copy(self._nfa.states),
                input_symbols=copy(self._nfa.symbols),
                start_state=copy(self._nfa.start_states),
                final_states=copy(self._nfa.final_states).union(final.elements),
            )
        )

    def get_start(self) -> "Set":
        return Set({state.value for state in self._nfa.start_states})

    def get_final(self) -> "Set":
        return Set({state.value for state in self._nfa.final_states})

    def get_labels(self) -> "Set":
        return Set({symbol.value for symbol in self._nfa.symbols})

    def get_nodes(self) -> "Set":
        return Set({state.value for state in self._nfa.states})

    def get_reachable(self) -> "Set":
        result = set()
        for s in self._nfa.start_states.intersection(self._nfa.final_states):
            result.add(Pair(s.value, s.value))
        decomposed = decompose_automaton(self._nfa)
        n = len(decomposed.states_to_index)
        m_sum = sum(decomposed.decomposition.values(), start=csr_matrix((n, n)))
        closure = transitive_closure(m_sum)

        start_indexes = {
            decomposed.states_to_index[state] for state in decomposed.start_states
        }
        finish_indexes = {
            decomposed.states_to_index[state] for state in decomposed.final_states
        }
        index_to_state = {v: k for k, v in decomposed.states_to_index.items()}
        for start, finish in closure:
            if start in start_indexes and finish in finish_indexes:
                result.add(
                    Pair(
                        index_to_state[start][0].value, index_to_state[finish][0].value
                    )
                )

        return Set(result)

    def get_edges(self) -> "Set":
        result = set()
        automation = self._nfa.to_dict()
        for start, item in automation.items():
            for label, end in item.items():
                for state in end:
                    result.add(Triple(start, label, state))
        return Set(result)

    def intersect(self, other: "Automation") -> "Automation":
        if isinstance(other, Automation):
            return Automation(fa_intersection(self._nfa, other._nfa))
        else:
            other.intersect(self)

    def union(self, other: "AutomationAbstract") -> "AutomationAbstract":
        if self._type != other.type:
            raise TypeError(
                "Expected set of type " + str(self._type) + ", got " + str(other.type)
            )
        if isinstance(other, Automation):
            return Automation(
                self._nfa.union(other._nfa).to_deterministic(), self._type
            )
        return other.union(self)

    def concat(self, other: "AutomationAbstract") -> "AutomationAbstract":
        if self._type != other.type:
            raise TypeError(
                "Expected set of type " + str(self._type) + ", got " + str(other.type)
            )
        if isinstance(other, Automation):
            return Automation(
                self._nfa.concatenate(other._nfa).to_deterministic(), self._type
            )
        return other.concat(self)

    def kleene(self) -> "AutomationAbstract":
        return Automation(self._nfa.kleene_star().to_deterministic(), self._type)


class ContextFreeGrammar(AutomationAbstract, ABC):
    def __init__(self, cfg: CFG):
        self._cfg = cfg
        self._type = Set({v.value for v in cfg.variables}).type
        self._rsm = ecfg_to_rsm(cfg_to_ecfg(cfg))

    def __str__(self):
        return self._cfg.to_text()

    @classmethod
    def from_str(cls, s: str) -> "ContextFreeGrammar":
        return cls(CFG.from_text(s))

    @classmethod
    def from_file(cls, path: str) -> "ContextFreeGrammar":
        return cls(cfg_from_file(path))

    def set_start(self, start: "Set") -> "AutomationAbstract":
        raise NotImplementedError("It is not possible to change start symbol of CFG")

    def set_final(self, final: "Set") -> "AutomationAbstract":
        raise NotImplementedError("It is not possible to change final symbol of CFG")

    def add_start(self, start: "Set") -> "AutomationAbstract":
        raise NotImplementedError("It is not possible to add start symbol to CFG")

    def add_final(self, final: "Set") -> "AutomationAbstract":
        raise NotImplementedError("It is not possible to add final symbol to CFG")

    def get_start(self) -> "Set":
        res = set()
        for v in self._rsm.automations[self._rsm.start_v].start_states:
            res.add(v.value)
        return Set(res)

    def get_final(self) -> "Set":
        res = set()
        for v in self._rsm.automations[self._rsm.start_v].final_states:
            res.add(v.value)
        return Set(res)

    def get_nodes(self) -> "Set":
        res = set()
        for automata in self._rsm.automations.values():
            for v in automata.states:
                res.add(v.value)
        return Set(res)

    def intersect(self, other: "ContextFreeGrammar") -> "ContextFreeGrammar":
        if isinstance(other, ContextFreeGrammar):
            return ContextFreeGrammar(self._cfg.intersection(other._cfg))
        raise TypeError("Expected ContextFreeGrammar, got " + str(type(other)))

    def concat(self, other: "ContextFreeGrammar") -> "ContextFreeGrammar":
        if isinstance(other, ContextFreeGrammar):
            return ContextFreeGrammar(self._cfg.concatenate(other._cfg))
        raise TypeError("Expected ContextFreeGrammar, got " + str(type(other)))

    def union(self, other: "ContextFreeGrammar") -> "ContextFreeGrammar":
        if isinstance(other, ContextFreeGrammar):
            return ContextFreeGrammar(self._cfg.union(other._cfg))
        raise TypeError("Expected ContextFreeGrammar, got " + str(type(other)))
