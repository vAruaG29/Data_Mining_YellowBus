"""
Graph utilities for parsing and handling graph datasets.
"""

import networkx as nx
from typing import List, Tuple, Dict


class Graph:
    
    def __init__(self):
        self.nodes = {}  
        self.edges = []  
        self.graph_id = None
        
    def add_node(self, node_id: int, label: int):

        self.nodes[node_id] = label
        
    def add_edge(self, src: int, dst: int, label: int):

        self.edges.append((src, dst, label))
        
    def to_networkx(self) -> nx.Graph:

        G = nx.Graph()
        for node_id, label in self.nodes.items():
            G.add_node(node_id, label=label)
        for src, dst, edge_label in self.edges:
            G.add_edge(src, dst, label=edge_label)
        return G
    
    def get_canonical_string(self) -> str:

        nodes_str = ','.join(f"{nid}:{label}" for nid, label in sorted(self.nodes.items()))
        edges_str = ','.join(f"{src}-{dst}:{label}" for src, dst, label in sorted(self.edges))
        return f"N[{nodes_str}]E[{edges_str}]"
    
    def __eq__(self, other):

        if not isinstance(other, Graph):
            return False
        return self.get_canonical_string() == other.get_canonical_string()
    
    def __hash__(self):

        return hash(self.get_canonical_string())


def parse_graph_file(filepath: str) -> List[Graph]:

    graphs = []
    current_graph = None
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            
            if line.startswith('#'):

                if current_graph is not None and len(current_graph.nodes) > 0:
                    graphs.append(current_graph)

                    if len(graphs) % 50 == 0:
                        print(f"  Parsed {len(graphs)} graphs...")

                current_graph = Graph()
                current_graph.graph_id = len(graphs)
                
            elif line.startswith('v '):

                parts = line.split()
                node_id = int(parts[1])
                label = int(parts[2])
                current_graph.add_node(node_id, label)
                
            elif line.startswith('e '):

                parts = line.split()
                src = int(parts[1])
                dst = int(parts[2])
                label = int(parts[3])
                current_graph.add_edge(src, dst, label)
    

    if current_graph is not None and len(current_graph.nodes) > 0:
        graphs.append(current_graph)
    
    return graphs


def remove_duplicates(graphs: List[Graph]) -> List[Graph]:
    
    seen = set()
    unique_graphs = []
    
    for graph in graphs:
        canon = graph.get_canonical_string()
        if canon not in seen:
            seen.add(canon)
            unique_graphs.append(graph)
    
    return unique_graphs


def save_graphs(graphs: List[Graph], filepath: str):

    with open(filepath, 'w') as f:
        for graph in graphs:
            f.write('#\n')
            for node_id, label in sorted(graph.nodes.items()):
                f.write(f'v {node_id} {label}\n')
            for src, dst, edge_label in sorted(graph.edges):
                f.write(f'e {src} {dst} {edge_label}\n')


def graph_to_dict(graph: Graph) -> dict:

    return {
        'nodes': graph.nodes,
        'edges': graph.edges,
        'graph_id': graph.graph_id
    }


def dict_to_graph(d: dict) -> Graph:

    g = Graph()
    g.nodes = d['nodes']
    g.edges = d['edges']
    g.graph_id = d.get('graph_id')
    return g
