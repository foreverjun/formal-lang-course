import os

from project.parser.parser import check, get_parser, save_dot

parser_correct = [
    "val x = 1;",
    "val asd = true;",
    "val asd = false;",
    "val asd = 0;",
    "val asd = -2131;",
    "val new_ = set_start({1, 2, 3}, gr);",
    "val numbers = { 1 , 2 , 3 , 4 , 5};",
    "val new_ = set_final({1 ,2 ,3 }, gr);",
    "val new_ = add_start({1 ,2 ,3 }, gr);",
    'val loader = load_graph("graph.txt");',
    'val reg = regex("a* b*");',
    'val g = cfg("S -> a S b | $");',
    "val inters = intersect(g1, g2);",
    "val inters = union(g1, g2);",
    "val reachi = get_reachable(g1);",
    "val v = get_nodes(g1);",
    "val v = filter([ i -> i], get_nodes (graph) );",
    "val m = map([i -> i], get_start (graph) );",
    "val nodes1 = filter ([ v -> v in s], ( map ([((u_g,u_q1),l,(v_g,v_q1)) -> u_g], get_edges (graph)) ));",
]

parser_incorrect = [
    "var x = 2;",
    "val x = 6",
    "val x = interse(g1, g2);",
    "val x = union(g1, );",
    "val x = union(g1, g2, g3);",
    "let x = 1;",
    "val x = ________ ;",
    "val x = 1, y = 2;",
]


def test_parser_correct():
    for code in parser_correct:
        assert check(code)
    for code in parser_incorrect:
        assert not check(code)


def test_save_dot():
    current_dir_path = os.path.dirname(os.path.realpath(__file__))
    path_actual = os.path.join(current_dir_path, "res", "parser_actual.dot")
    path_expected = os.path.join(current_dir_path, "res", "parser_expected.dot")
    parser_test = "val t = intersect (set_start(get_start(g2) , g1), g3);"
    save_dot(parser_test, path_actual)

    with open(path_expected, "r") as file:
        expected = file.read()

    with open(path_actual, "r") as file:
        actual = file.read()
        assert actual == expected
