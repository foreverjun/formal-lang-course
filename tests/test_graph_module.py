import os

from project import graph_module


def test_get_graph_metrics():
    nodes_num, edges_num, labels = graph_module.get_graph_metrics_by_name("bzip")
    assert nodes_num == 632
    assert edges_num == 556
    assert labels == {"a", "d"}


# Create and save graph with two cycles. After that load it and check their equality


def test_save_graph():
    current_dir_path = os.path.dirname(os.path.realpath(__file__))
    expected_path = os.path.join(current_dir_path, "expected.dot")
    actual_path = os.path.join(current_dir_path, "actual.dot")
    graph_module.generate_and_save_two_cycles_graph(4, 5, ("c", "d"), actual_path)
    with open(expected_path, "r") as expected_file:
        with open(actual_path, "r") as actual_file:
            assert expected_file.read() == actual_file.read()
