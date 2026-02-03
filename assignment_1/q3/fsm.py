

import networkx as nx
from collections import defaultdict, Counter
from typing import List, Set, Tuple, Dict, Optional
from graph_utils import Graph
import pickle


class PathPattern:

    
    def __init__(self, node_labels: Tuple = (), edge_labels: Tuple = ()):
        self.node_labels = node_labels 
        self.edge_labels = edge_labels  
        
    def __hash__(self):
        return hash((self.node_labels, self.edge_labels))
    
    def __eq__(self, other):
        return (self.node_labels, self.edge_labels) == (other.node_labels, other.edge_labels)
    
    def __str__(self):
        parts = []
        for i, nl in enumerate(self.node_labels):
            parts.append(str(nl))
            if i < len(self.edge_labels):
                parts.append(f"-{self.edge_labels[i]}-")
        return "".join(parts)
    
    def __repr__(self):
        return f"Path({self})"
    
    def __len__(self):
        return len(self.edge_labels)  
    
    def to_graph(self) -> Graph:

        g = Graph()
        for i, label in enumerate(self.node_labels):
            g.add_node(i, label)
        for i, edge_label in enumerate(self.edge_labels):
            g.add_edge(i, i+1, edge_label)
        return g
    
    def extend(self, node_label: int, edge_label: int, prepend: bool = False) -> 'PathPattern':

        if prepend:
            return PathPattern(
                (node_label,) + self.node_labels,
                (edge_label,) + self.edge_labels
            )
        else:
            return PathPattern(
                self.node_labels + (node_label,),
                self.edge_labels + (edge_label,)
            )
    
    def canonical_form(self) -> 'PathPattern':

        rev_nodes = tuple(reversed(self.node_labels))
        rev_edges = tuple(reversed(self.edge_labels))
        
        if (rev_nodes, rev_edges) < (self.node_labels, self.edge_labels):
            return PathPattern(rev_nodes, rev_edges)
        return self


class TreePattern:

    
    def __init__(self):
        self.nodes = {}  
        self.edges = []  
        self.adjacency = defaultdict(list)  
        
    def add_node(self, node_id: int, label: int):
        self.nodes[node_id] = label
        
    def add_edge(self, src: int, dst: int, label: int):
        self.edges.append((src, dst, label))
        self.adjacency[src].append((dst, label))
        self.adjacency[dst].append((src, label))
    
    def __hash__(self):

        return hash(self._canonical_tuple())
    
    def __eq__(self, other):
        return self._canonical_tuple() == other._canonical_tuple()
    
    def _canonical_tuple(self):

        if not self.nodes:
            return ()

        sorted_edges = tuple(sorted(
            (min(s,d), max(s,d), self.nodes.get(s,0), self.nodes.get(d,0), l) 
            for s, d, l in self.edges
        ))
        return sorted_edges
    
    def to_graph(self) -> Graph:

        g = Graph()
        for node_id, label in self.nodes.items():
            g.add_node(node_id, label)
        for src, dst, label in self.edges:
            g.add_edge(src, dst, label)
        return g


def extract_paths_from_graph(graph: nx.Graph, max_length: int = 5) -> Set[PathPattern]:
  
    paths = set()
    
    def get_label(node):
        return graph.nodes[node].get('label', 0)
    
    def get_edge_label(u, v):
        return graph[u][v].get('label', 0)
    

    for start_node in graph.nodes():

        stack = [(start_node, [start_node], set([start_node]))]
        
        while stack:
            current, path_nodes, visited = stack.pop()
            

            if len(path_nodes) > 1:
                node_labels = tuple(get_label(n) for n in path_nodes)
                edge_labels = tuple(
                    get_edge_label(path_nodes[i], path_nodes[i+1]) 
                    for i in range(len(path_nodes)-1)
                )
                pattern = PathPattern(node_labels, edge_labels).canonical_form()
                paths.add(pattern)
            

            if len(path_nodes) - 1 < max_length:
                for neighbor in graph.neighbors(current):
                    if neighbor not in visited:
                        new_visited = visited | {neighbor}
                        new_path = path_nodes + [neighbor]
                        stack.append((neighbor, new_path, new_visited))
    
    return paths


def extract_trees_from_graph(graph: nx.Graph, max_edges: int = 5) -> Set[TreePattern]:
  
    trees = set()
    
    def get_label(node):
        return graph.nodes[node].get('label', 0)
    
    def get_edge_label(u, v):
        return graph[u][v].get('label', 0)
    

    for center in graph.nodes():
        neighbors = list(graph.neighbors(center))
        if len(neighbors) >= 2:  

            for i in range(len(neighbors)):
                for j in range(i+1, min(i+4, len(neighbors))):  
                    tree = TreePattern()
                    tree.add_node(0, get_label(center))
                    
                    n1, n2 = neighbors[i], neighbors[j]
                    tree.add_node(1, get_label(n1))
                    tree.add_node(2, get_label(n2))
                    tree.add_edge(0, 1, get_edge_label(center, n1))
                    tree.add_edge(0, 2, get_edge_label(center, n2))
                    
                    trees.add(tree)
    
    return trees


def gaston_mine_patterns(graphs: List[Graph], min_support: int = 2, 
                         max_path_length: int = 4, include_trees: bool = True) -> Dict:
    

    path_counts = Counter()
    path_occurrences = defaultdict(set)
    
    try:
        from joblib import Parallel, delayed
        import multiprocessing
        

        n_jobs = min(multiprocessing.cpu_count(), 4)
        
        CHUNK_SIZE = 5000  
        n_graphs = len(graphs)
        n_chunks = (n_graphs + CHUNK_SIZE - 1) // CHUNK_SIZE
        

        
        def process_graph_paths(idx, graph, max_length):
            nx_graph = graph.to_networkx()
            paths = extract_paths_from_graph(nx_graph, max_length)

            return [(hash(p), p, idx) for p in paths]
        

        for chunk_idx in range(n_chunks):
            start_idx = chunk_idx * CHUNK_SIZE
            end_idx = min(start_idx + CHUNK_SIZE, n_graphs)
            chunk_graphs = graphs[start_idx:end_idx]
            
            if n_chunks > 1:
                print(f"  Chunk {chunk_idx + 1}/{n_chunks} (graphs {start_idx}-{end_idx-1})...")
            

            chunk_results = Parallel(n_jobs=n_jobs, verbose=5)(
                delayed(process_graph_paths)(start_idx + i, g, max_path_length)
                for i, g in enumerate(chunk_graphs)
            )
            

            for graph_paths in chunk_results:
                seen = set()  
                for _, pattern, idx in graph_paths:
                    if pattern not in seen:
                        path_counts[pattern] += 1
                        path_occurrences[pattern].add(idx)
                        seen.add(pattern)
            

            del chunk_results
        
    except ImportError:

        for idx, graph in enumerate(graphs):
            if idx % 100 == 0:
                print(f"  Processing graph {idx}/{len(graphs)}...")
            
            nx_graph = graph.to_networkx()
            paths = extract_paths_from_graph(nx_graph, max_path_length)
            
            for pattern in paths:
                path_counts[pattern] += 1
                path_occurrences[pattern].add(idx)
    
    frequent_paths = {p: c for p, c in path_counts.items() if c >= min_support}

    
    frequent_trees = {}
    tree_occurrences = {}
    
    if include_trees:

        tree_counts = Counter()
        tree_occurrences = defaultdict(set)
        
        try:
            def process_graph_trees(idx, graph, max_edges):
                nx_graph = graph.to_networkx()
                trees = extract_trees_from_graph(nx_graph, max_edges)
                return [(t, idx) for t in trees]
            
            results = Parallel(n_jobs=n_jobs, verbose=5)(
                delayed(process_graph_trees)(idx, g, max_path_length)
                for idx, g in enumerate(graphs)
            )
            
            for graph_trees in results:
                seen = set()
                for pattern, idx in graph_trees:
                    if pattern not in seen:
                        tree_counts[pattern] += 1
                        tree_occurrences[pattern].add(idx)
                        seen.add(pattern)
                        
        except:
            for idx, graph in enumerate(graphs):
                if idx % 100 == 0:
                    print(f"  Processing graph {idx}/{len(graphs)}...")
                
                nx_graph = graph.to_networkx()
                trees = extract_trees_from_graph(nx_graph, max_path_length)
                
                for pattern in trees:
                    tree_counts[pattern] += 1
                    tree_occurrences[pattern].add(idx)
        
        frequent_trees = {t: c for t, c in tree_counts.items() if c >= min_support}

    

    
    return {
        'paths': frequent_paths,
        'path_occurrences': path_occurrences,
        'trees': frequent_trees,
        'tree_occurrences': tree_occurrences
    }


def calculate_information_gain(freq: int, n_graphs: int) -> float:

    import math
    
    if freq == 0 or freq == n_graphs:
        return 0.0
    
    p_present = freq / n_graphs
    p_absent = 1 - p_present
    
    if p_present > 0 and p_absent > 0:
        entropy = -p_present * math.log2(p_present) - p_absent * math.log2(p_absent)
    else:
        entropy = 0.0
    
    frequency_weight = min(p_present, p_absent) * 2
    return entropy * frequency_weight * freq


def calculate_overlap(sg1_graphs: set, sg2_graphs: set) -> float:

    if not sg1_graphs or not sg2_graphs:
        return 0.0
    
    intersection = len(sg1_graphs & sg2_graphs)
    union = len(sg1_graphs | sg2_graphs)
    
    return intersection / union if union > 0 else 0.0


def select_discriminative_patterns(patterns_result: Dict, k: int, n_graphs: int,
                                    overlap_threshold: float = 0.5) -> List[Graph]:
   
    

    all_patterns = []
    all_occurrences = {}
    

    for pattern, freq in patterns_result['paths'].items():
        ig = calculate_information_gain(freq, n_graphs)
        all_patterns.append((pattern, ig, freq, 'path'))
        all_occurrences[pattern] = patterns_result['path_occurrences'].get(pattern, set())
    

    for pattern, freq in patterns_result['trees'].items():
        ig = calculate_information_gain(freq, n_graphs)
        all_patterns.append((pattern, ig, freq, 'tree'))
        all_occurrences[pattern] = patterns_result['tree_occurrences'].get(pattern, set())
    

    all_patterns.sort(key=lambda x: x[1], reverse=True)
    

    for i, (pattern, score, freq, ptype) in enumerate(all_patterns[:10]):
        print(f"  {i+1}. [{ptype}] Freq: {freq}/{n_graphs} ({freq/n_graphs*100:.1f}%), IG: {score:.4f}")
    

    selected = []
    selected_graph_sets = []
    
    for pattern, score, freq, ptype in all_patterns:
        if len(selected) >= k:
            break
        
        pattern_graphs = all_occurrences.get(pattern, set())
        

        is_diverse = True
        for existing_graphs in selected_graph_sets:
            if calculate_overlap(pattern_graphs, existing_graphs) > overlap_threshold:
                is_diverse = False
                break
        
        if is_diverse:
            selected.append((pattern, score, freq, ptype))
            selected_graph_sets.append(pattern_graphs)
    

    if len(selected) < k:
        selected_set = {id(s[0]) for s in selected}
        for pattern, score, freq, ptype in all_patterns:
            if len(selected) >= k:
                break
            if id(pattern) not in selected_set:
                selected.append((pattern, score, freq, ptype))
                selected_set.add(id(pattern))
    

    path_count = sum(1 for s in selected if s[3] == 'path')
    tree_count = sum(1 for s in selected if s[3] == 'tree')

    

    result_graphs = []
    for pattern, _, _, ptype in selected:
        result_graphs.append(pattern.to_graph())
    
    return result_graphs


def select_discriminative_subgraphs(graphs: List[Graph], k: int = 50, 
                                     max_size: int = 5) -> List[Graph]:
   
    n_graphs = len(graphs)
    

    min_support = max(2, int(0.20 * n_graphs))
    
    print(f"\n{'='*60}")
    print(f"GASTON Frequent Subgraph Mining")
    print(f"{'='*60}")
    print(f"Graphs: {n_graphs}, k: {k}, max_size: {max_size}")
    print(f"Minimum support: {min_support} ({min_support/n_graphs*100:.1f}%)")
    

    patterns_result = gaston_mine_patterns(
        graphs, 
        min_support=min_support,
        max_path_length=max_size,
        include_trees=True  
    )
    overlap_threshold = 0.8

    if n_graphs > 10000:
        overlap_threshold = 0.7  
    else:
        overlap_threshold = 0.8  

    
    selected_graphs = select_discriminative_patterns(
        patterns_result, 
        k=k, 
        n_graphs=n_graphs,
        overlap_threshold=overlap_threshold
    )
    

    
    return selected_graphs


def save_subgraphs(subgraphs: List[Graph], filepath: str):

    with open(filepath, 'wb') as f:
        pickle.dump(subgraphs, f)



def load_subgraphs(filepath: str) -> List[Graph]:

    with open(filepath, 'rb') as f:
        subgraphs = pickle.load(f)

    return subgraphs
