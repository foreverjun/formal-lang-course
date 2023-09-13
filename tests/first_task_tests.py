from project import graph_module
import networkx as nx
import pathlib


def get_graph_metrics_test():
    nodes_num, edges_num, labels = graph_module.get_graph_metrics_by_name(bzip)
    assert nodes_num == 632
    assert edges_num == 556
    assert labels == {"a", "b"}


# Create and save graph with two cycles. After that load it and check their equality


def save_graph_test():
    graph_module.generate_and_save_two_cycles_graph(4, 5, ("c", "d"), "actual.dot")
    current_dir = pathlib.Path().resolve()
    expected_path = pathlib.Path(current_dir, "expected.dot")
    actual_path = pathlib.Path(current_dir, "actual.dot")
    with open(expected_path, "r") as expected_file:
        with open(actual_path, "r") as actual_file:
            assert expected_file.read() == actual_file.read()
