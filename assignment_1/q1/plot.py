import csv
import matplotlib.pyplot as plt
import sys
import os

def generate_plot(csv_path, output_dir):
    data = {}

    try:
        with open(csv_path, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                alg = row['Algorithm']
                sup = float(row['Support'])
                time = float(row['TimeSeconds'])

                if alg not in data:
                    data[alg] = {'supports': [], 'times': []}
                
                data[alg]['supports'].append(sup)
                data[alg]['times'].append(time)

        plt.figure(figsize=(10, 6))

        for alg, values in data.items():
            sorted_pairs = sorted(
                zip(values['supports'], values['times']),
                reverse=True
            )
            supports, times = zip(*sorted_pairs)

            plt.plot(supports, times, marker='o', linewidth=2, label=alg)

        # REAL (linear) scale
        plt.xlabel('Support Threshold (%)')
        plt.ylabel('Execution Time (Seconds)')
        plt.title('Performance Comparison: Apriori vs FP-Growth')

        plt.gca().invert_xaxis()
        plt.legend()
        plt.grid(True)

        plot_path = os.path.join(output_dir, 'plot.png')
        plt.savefig(plot_path)
        print(f"Successfully generated plot at: {plot_path}")

    except Exception as e:
        print(f"Error generating plot: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 plot_results.py <csv_path> <output_dir>")
    else:
        generate_plot(sys.argv[1], sys.argv[2])
