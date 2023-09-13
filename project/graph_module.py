from typing import Tuple

import cfpq_data
import networkx as nx


def get_graph(name: str) -> nx.MultiDiGraph:
    gr_path = cfpq_data.download(name)
    return cfpq_data.graph_from_csv(gr_path)


def get_graph_metrics(graph: nx.MultiDiGraph) -> Tuple[int, int, set]:
    nodes_num: int = graph.number_of_nodes()
    edges_num: int = graph.number_of_edges()
    # getting set of edge labels
    labels = set()
    for edge in graph.edges(data="label"):
        labels.add(edge[2])
    return nodes_num, edges_num, labels


def get_graph_metrics_by_name(name: str) -> Tuple[int, int, set]:
    graph = get_graph(name)
    return get_graph_metrics(graph)


# first_cycle_num : The number of nodes in the first cycle without a common node
# second_cycle_num : The number of nodes in the second cycle without a common node
def generate_and_save_two_cycles_graph(
    first_cycle_num: int, second_cycle_num: int, labels: Tuple[str, str], path: str
):
    graph = nx.labeled_two_cycles_graph(
        first_cycle_num, second_cycle_num, labels=labels
    )
    nx.nx_pydot.write_dot(graph, path)
