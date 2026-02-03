import matplotlib.pyplot as plt
import sys
import os

def plot_results(results_file, output_dir):
    supports = []
    times = {'gspan': [], 'fsg': [], 'gaston': []}

    try:
        with open(results_file, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 3:
                    algo = parts[0]
                    supp = int(parts[1])
                    runtime = float(parts[2])
                    
                    if supp not in supports:
                        supports.append(supp)
                    
                    if algo in times:
                        times[algo].append((supp, runtime))
    except FileNotFoundError:
        print("Results file not found.")
        return

    supports.sort()
    
    plt.figure(figsize=(10, 6))
    
    markers = {'gspan': 'o', 'fsg': 's', 'gaston': '^'}
    colors = {'gspan': 'blue', 'fsg': 'red', 'gaston': 'green'}
    labels = {'gspan': 'gSpan', 'fsg': 'FSG', 'gaston': 'Gaston'}

    for algo in ['gspan', 'fsg', 'gaston']:
        data = sorted(times[algo], key=lambda x: x[0])
        x_vals = [d[0] for d in data]
        y_vals = [d[1] for d in data]
        
        plt.plot(x_vals, y_vals, marker=markers[algo], color=colors[algo], label=labels[algo], linestyle='-')

    plt.title('Runtime Comparison of Frequent Subgraph Mining Algorithms')
    plt.xlabel('Minimum Support (%)')
    plt.ylabel('Runtime (seconds)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    output_path = os.path.join(output_dir, 'plot.png')
    plt.savefig(output_path)
    print(f"Plot saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python plot.py <results_file> <output_dir>")
        sys.exit(1)
        
    plot_results(sys.argv[1], sys.argv[2])