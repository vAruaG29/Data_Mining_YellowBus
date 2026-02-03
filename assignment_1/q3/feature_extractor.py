
import networkx as nx
import numpy as np
from typing import List
from graph_utils import Graph
from fsm import load_subgraphs


def is_subgraph_isomorphic(pattern: Graph, target: Graph) -> bool:
   
    if len(pattern.nodes) > len(target.nodes):
        return False
    if len(pattern.edges) > len(target.edges):
        return False
    

    try:
        import rustworkx as rx
        from rustworkx import is_subgraph_isomorphic as rx_is_subgraph
        

        pattern_rx = rx.PyGraph()
        target_rx = rx.PyGraph()
        

        pattern_node_map = {}
        for node_id, label in pattern.nodes.items():
            pattern_node_map[node_id] = pattern_rx.add_node(label)
        
        target_node_map = {}
        for node_id, label in target.nodes.items():
            target_node_map[node_id] = target_rx.add_node(label)
        

        for src, dst, label in pattern.edges:
            pattern_rx.add_edge(pattern_node_map[src], pattern_node_map[dst], label)
        
        for src, dst, label in target.edges:
            target_rx.add_edge(target_node_map[src], target_node_map[dst], label)
        

        def node_match(n1, n2):
            return n1 == n2
        
        def edge_match(e1, e2):
            return e1 == e2
        
        return rx_is_subgraph(
            target_rx, pattern_rx,
            node_matcher=node_match,
            edge_matcher=edge_match,
            induced=False  
        )
        
    except ImportError:
        pass
    

    pattern_nx = pattern.to_networkx()
    target_nx = target.to_networkx()
    

    def node_match(n1, n2):
        return n1.get('label') == n2.get('label')
    

    def edge_match(e1, e2):
        return e1.get('label') == e2.get('label')
    

    GM = nx.isomorphism.GraphMatcher(
        target_nx,
        pattern_nx,
        node_match=node_match,
        edge_match=edge_match
    )
    

    return GM.subgraph_is_monomorphic()


def extract_features(graphs: List[Graph], subgraphs: List[Graph]) -> np.ndarray:
  
    n_graphs = len(graphs)
    n_features = len(subgraphs)
    

    
    try:
        from joblib import Parallel, delayed
        import multiprocessing
        n_jobs = min(multiprocessing.cpu_count(), 8)  

        
        def extract_single_graph_features(graph, subgraphs):
            """Extract binary features for a single graph."""
            features = []
            for subgraph in subgraphs:
                if is_subgraph_isomorphic(subgraph, graph):
                    features.append(1)
                else:
                    features.append(0)
            return features
        

        results = Parallel(n_jobs=n_jobs, verbose=10)(
            delayed(extract_single_graph_features)(graph, subgraphs) 
            for graph in graphs
        )
        

        features = np.array(results, dtype=np.int8)

        
    except ImportError:

        features = np.zeros((n_graphs, n_features), dtype=np.int8)
        
        for i, graph in enumerate(graphs):
            if i % 50 == 0:
                print(f"  Extracting features for graph {i}/{n_graphs}...")
            
            for j, subgraph in enumerate(subgraphs):
                if is_subgraph_isomorphic(subgraph, graph):
                    features[i, j] = 1
    

    
    return features


def save_features(features: np.ndarray, filepath: str):

    np.save(filepath, features)



def load_features(filepath: str) -> np.ndarray:

    features = np.load(filepath)

    return features
