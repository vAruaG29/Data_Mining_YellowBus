import sys

def parse_and_convert(input_path, output_prefix):
    try:
        with open(input_path, 'r') as f:
            lines = [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        print(f"Error: File {input_path} not found.")
        sys.exit(1)

    graphs = []
    i = 0
    
    label_map = {}
    next_label_id = 0

    def get_label_id(label_str):
        nonlocal next_label_id
        if label_str not in label_map:
            label_map[label_str] = next_label_id
            next_label_id += 1
        return label_map[label_str]

    while i < len(lines):
        line = lines[i]
        
        if line.startswith("#"):
            graph_id = line.replace("#", "").strip()
            i += 1
            
            try:
                if i >= len(lines): break
                num_nodes = int(lines[i])
                i += 1
            except ValueError:
                continue

            nodes = []
            for node_idx in range(num_nodes):
                if i < len(lines):
                    raw_label = lines[i]
                    lbl_id = get_label_id(raw_label)
                    nodes.append((node_idx, lbl_id))
                    i += 1
            
            edges = []
            if i < len(lines):
                try:
                    if lines[i].startswith("#"):
                        pass
                    else:
                        num_edges = int(lines[i])
                        i += 1
                        
                        for _ in range(num_edges):
                            if i < len(lines):
                                parts = lines[i].split()
                                if len(parts) >= 3:
                                    try:
                                        u, v = int(parts[0]), int(parts[1])
                                        label = parts[2]
                                        edge_lbl_id = get_label_id(label)
                                        
                                        if u < num_nodes and v < num_nodes:
                                            if u > v:
                                                u, v = v, u
                                            edges.append((u, v, edge_lbl_id))
                                    except ValueError:
                                        pass
                                i += 1
                except ValueError:
                    pass

            if len(nodes) > 0:
                graphs.append({
                    "id": graph_id,
                    "nodes": nodes,
                    "edges": edges
                })
        else:
            i += 1

    gspan_file = f"{output_prefix}.gspan"
    with open(gspan_file, 'w') as f:
        for g in graphs:
            f.write(f"t # {g['id']}\n")
            for n_id, n_lbl in g['nodes']:
                f.write(f"v {n_id} {n_lbl}\n")
            
            unique_edges = sorted(list(set(g['edges'])))
            for u, v, lbl in unique_edges:
                f.write(f"e {u} {v} {lbl}\n")
            
    fsg_file = f"{output_prefix}.fsg"
    with open(fsg_file, 'w') as f:
        for g in graphs:
            f.write(f"t # {g['id']}\n")
            for n_id, n_lbl in g['nodes']:
                f.write(f"v {n_id} {n_lbl}\n")
            
            unique_edges = sorted(list(set(g['edges'])))
            for u, v, lbl in unique_edges:
                f.write(f"u {u} {v} {lbl}\n")
    
    print(len(graphs))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert.py <input> <output_prefix>")
        sys.exit(1)
    parse_and_convert(sys.argv[1], sys.argv[2])