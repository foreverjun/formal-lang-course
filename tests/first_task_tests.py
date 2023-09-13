from project import graph_module
import networkx as nx


def get_graph_metrics_test():
    nodes_num, edges_num, labels = graph_module.get_graph_metrics_by_name(bzip)
    assert nodes_num == 632
    assert edges_num == 556
    assert labels == {"a", "b"}


# Create and save graph with two cycles. After that load it and check their equality


def save_graph_test():
    graph_module.generate_and_save_two_cycles_graph(3, 4, ("c", "d"), "test.dot")
    graph = nx.nx_pydot.read_dot("test.dot")
    actual_graph = nx.labeled_two_cycles_graph(3, 4, labels=("c", "d"))
    assert nx.is_isomorphic(graph, actual_graph)
