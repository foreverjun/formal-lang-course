import os

from pyformlang.cfg import Variable, Terminal

from project.task_6 import *


def test_empty_file():
    cfg = cfg_from_file("tests/test_files/empty_file")
    weak = cfg_to_weak_cnf(cfg)
    assert cfg.is_empty()
    assert weak.is_empty()


def is_wcnf(cfg: CFG):
    for prod in cfg.productions:
        if len(prod.body) == 1:
            if not isinstance(prod.body[0], Terminal):
                return False
        elif len(prod.body) == 2:
            if not isinstance(prod.body[0], Variable) or not isinstance(
                prod.body[1], Variable
            ):
                return False
        elif len(prod.body) == 0:
            return True
    return True


def test_cfg_from_file():
    current_dir_path = os.path.dirname(os.path.realpath(__file__))
    expected = CFG().from_text("S -> a S b | a b", "S")
    actual = cfg_from_file(os.path.join(current_dir_path, "res", "cfg_1"))
    words = ["ab", "aaabbb", "aabb", "aaaabbbb"]
    for word in words:
        assert expected.contains(word)
        assert actual.contains(word)
    assert actual.productions == expected.productions
    assert actual.start_symbol == expected.start_symbol


def test_cfg_from_file_2():
    #     more complex cfg with 6 productions and 4 variables
    current_dir_path = os.path.dirname(os.path.realpath(__file__))
    expected = CFG().from_text(
        "S -> A B | B C\n A -> a A | a\n B -> b B | b\n C -> c C | c", "S"
    )
    actual = cfg_from_file(os.path.join(current_dir_path, "res", "cfg_2"), "S")
    words = ["ab", "aabb", "bbcc", "bbbbccc", "aabbbb"]
    for word in words:
        assert expected.contains(word)
        assert actual.contains(word)
    assert actual.productions == expected.productions
    assert actual.start_symbol == expected.start_symbol


def test_cfg_to_weak_cnf():
    cfg = CFG.from_text(
        "S -> A B | B C\n A -> a A | a\n B -> b B | b\n C -> c C | c", "S"
    )
    weak = cfg_to_weak_cnf(cfg)
    assert is_wcnf(weak)
    words = ["ab", "aabb", "bbcc", "bbbbccc", "aabbbb"]
    for word in words:
        assert weak.contains(word)
        assert cfg.contains(word)


def test_cfg_to_weak_cnf_2_with_unit_productions():
    cfg = CFG.from_text(
        "S -> a A | b B | c C | d D\n A -> a A | b B | c C | d\n B -> a A | b B | c | d D\n C -> a A | b | c C | d D\n D -> a | b B | c C | d D\n S -> $",
        "S",
    )
    weak = cfg_to_weak_cnf(cfg)
    assert is_wcnf(weak)
    words = ["aaabbbda", "abc", "aabbc", "bbc", "cccaabda"]
    for word in words:
        assert cfg.contains(word)
        assert weak.contains(word)
