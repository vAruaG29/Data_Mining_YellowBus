

import sys
from graph_utils import parse_graph_file, remove_duplicates
from fsm import load_subgraphs
from feature_extractor import extract_features, save_features


def main():
    if len(sys.argv) != 4:
        print("Usage: python convert_to_features.py <path_graphs> <path_discriminative_subgraphs> <path_features>")
        sys.exit(1)
    
    graphs_path = sys.argv[1]
    subgraphs_path = sys.argv[2]
    output_path = sys.argv[3]
    

    

    graphs = parse_graph_file(graphs_path)

    

    unique_graphs = remove_duplicates(graphs)

    

    subgraphs = load_subgraphs(subgraphs_path)
    

    features = extract_features(unique_graphs, subgraphs)
    

    save_features(features, output_path)
    
  


if __name__ == "__main__":
    main()
