from dataclasses import dataclass
from project.parser.interpreter.tuples import *


@dataclass
class Pat:
    pass


@dataclass
class PatVar(Pat):
    name: str


@dataclass
class PatPair(Pat):
    first: Pat
    second: Pat


@dataclass
class PatTriple(Pat):
    first: Pat
    second: Pat
    third: Pat


def match(pat: Pat, value):
    if isinstance(pat, PatVar):
        return {pat.name: value}
    elif isinstance(pat, PatPair):
        if isinstance(value, Pair):
            return {**match(pat.first, value.start), **match(pat.second, value.end)}
        else:
            return None
    elif isinstance(pat, PatTriple):
        if isinstance(value, Triple):
            return {
                **match(pat.first, value.start),
                **match(pat.second, value.end),
                **match(pat.third, value.label),
            }
    else:
        raise TypeError("Invalid pattern type")
