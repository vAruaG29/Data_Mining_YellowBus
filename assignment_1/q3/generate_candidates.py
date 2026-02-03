

import sys
import numpy as np


def generate_candidates(db_features: np.ndarray, query_features: np.ndarray) -> dict:
  
    n_queries = query_features.shape[0]
    n_db_graphs = db_features.shape[0]
    
    
    candidates = {}
    
    for q_idx in range(n_queries):
        query_vec = query_features[q_idx]
        candidate_list = []
        

        for db_idx in range(n_db_graphs):
            db_vec = db_features[db_idx]
            
            if np.all(query_vec <= db_vec):
                candidate_list.append(db_idx)  
        
        candidates[q_idx] = candidate_list  
        
        if (q_idx + 1) % 10 == 0:
            print(f"Processed query {q_idx + 1}/{n_queries}")
    
    return candidates


def save_candidates(candidates: dict, filepath: str):
   
    with open(filepath, 'w') as f:
        for query_id in sorted(candidates.keys()):
            candidate_list = candidates[query_id]
            f.write(f"q # {query_id}\n")
            f.write(f"c # {' '.join(map(str, candidate_list))}\n")
    


def print_statistics(candidates: dict, db_features: np.ndarray):

    n_db_graphs = db_features.shape[0]
    
    total_queries = len(candidates)
    total_candidates = sum(len(cands) for cands in candidates.values())
    avg_candidates = total_candidates / total_queries if total_queries > 0 else 0
    
    min_candidates = min(len(cands) for cands in candidates.values()) if candidates else 0
    max_candidates = max(len(cands) for cands in candidates.values()) if candidates else 0
    
    print("\n" + "=" * 60)
    print("Candidate Set Statistics")
    print("=" * 60)
    print(f"Total queries: {total_queries}")
    print(f"Total database graphs: {n_db_graphs}")
    print(f"Average candidates per query: {avg_candidates:.2f}")
    print(f"Min candidates: {min_candidates}")
    print(f"Max candidates: {max_candidates}")
    print(f"Average filtering ratio: {(1 - avg_candidates/n_db_graphs)*100:.2f}%")
    print("=" * 60)


def compute_scores(candidates: dict, query_graphs, db_graphs, verbose: bool = True):
   
    import sys
    sys.path.insert(0, '.')
    from feature_extractor import is_subgraph_isomorphic
    
    scores = {}
    total_rq = 0
    total_cq = 0
    
    if verbose:
        print("\n" + "=" * 60)
        print("Performance Metric: sq = |Rq| / |Cq|")
        print("=" * 60)
        print(f"{'Query':<8} {'|Cq|':<8} {'|Rq|':<8} {'sq':<10} {'Status'}")
        print("-" * 60)
    
    for q_idx, (q_id, cand_list) in enumerate(sorted(candidates.items())):
        query = query_graphs[q_idx]
        
        cq = len(cand_list)
        rq = 0
        
        for db_id in cand_list:
            db_graph = db_graphs[db_id]  
            if is_subgraph_isomorphic(query, db_graph):
                rq += 1
        
        sq = rq / cq if cq > 0 else 0.0
        
        scores[q_id] = {
            'Cq': cq,
            'Rq': rq,
            'sq': sq
        }
        
        total_rq += rq
        total_cq += cq
        
        if sq >= 0.5:
            status = "GOOD ✓"
        elif sq >= 0.2:
            status = "OK"
        else:
            status = "NEEDS IMPROVEMENT"
        
        if verbose:
            print(f"q # {q_id:<4} {cq:<8} {rq:<8} {sq:<10.4f} {status}")
    
    avg_sq = sum(s['sq'] for s in scores.values()) / len(scores) if scores else 0
    avg_rq = total_rq / len(scores) if scores else 0
    avg_cq = total_cq / len(scores) if scores else 0
    
    if verbose:
        print("-" * 60)
        print(f"{'AVG':<8} {avg_cq:<8.1f} {avg_rq:<8.1f} {avg_sq:<10.4f}")
        print("=" * 60)
        print(f"\nHigher sq is better (means smaller candidate sets)")
        print(f"Perfect score is 1.0 (Cq = Rq, no false positives)")
    
    return {
        'per_query': scores,
        'avg_sq': avg_sq,
        'avg_Rq': avg_rq,
        'avg_Cq': avg_cq,
        'total_Rq': total_rq,
        'total_Cq': total_cq
    }


def main():
    if len(sys.argv) != 4:
        print("Usage: python generate_candidates.py <path_database_graph_features> <path_query_graph_features> <path_out_file>")
        sys.exit(1)
    
    db_features_path = sys.argv[1]
    query_features_path = sys.argv[2]
    output_path = sys.argv[3]
    

    db_features = np.load(db_features_path)

    query_features = np.load(query_features_path)

    candidates = generate_candidates(db_features, query_features)
    
    print_statistics(candidates, db_features)
    
    save_candidates(candidates, output_path)
    


if __name__ == "__main__":
    main()
