"""
Main script for identifying discriminative subgraphs from database graphs.
"""

import sys
from graph_utils import parse_graph_file, remove_duplicates
from fsm import select_discriminative_subgraphs, save_subgraphs


def main():
    if len(sys.argv) != 3:
        print("Usage: python identify_subgraphs.py <path_graph_dataset> <path_discriminative_subgraphs>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    graphs = parse_graph_file(input_path)


    unique_graphs = remove_duplicates(graphs)
    
    k = 50  
    max_size = 9  
    
    discriminative_subgraphs = select_discriminative_subgraphs(
        unique_graphs,
        k=k,
        max_size=max_size
    )
    
    save_subgraphs(discriminative_subgraphs, output_path)


if __name__ == "__main__":
    main()
