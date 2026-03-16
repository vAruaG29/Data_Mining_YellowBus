import sys
import urllib.request
import json
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import warnings

# Suppress sklearn warnings (e.g., memory leak on Windows or n_init warnings)
warnings.filterwarnings("ignore")

def load_data(arg):
    """
    Loads data either from a .npy file or from the dataset API.
    """
    if str(arg).endswith('.npy'):
        # Mode 2: Read from .npy file
        return np.load(arg)
    else:
        # Mode 1: Fetch from API using dataset_num
        dataset_num = arg
        
        # NOTE: The assignment says "dataset specific to your kerberos id". 
        student_id = "cs5221138"
        
        url = f"http://hulk.cse.iitd.ac.in:3000/dataset?student_id={student_id}&dataset_num={dataset_num}"
        
        
        try:
            with urllib.request.urlopen(url) as response:
                raw_data = response.read().decode('utf-8')
                data = json.loads(raw_data)
                return np.array(data["X"])
        except Exception as e:
            print(f"Failed to fetch data from API: {e}", file=sys.stderr)
            print("Make sure you are connected to the IIT network.", file=sys.stderr)
            sys.exit(1)

def compute_kmeans(X):
    """
    Computes k-means for k in {1..15} and records the objective value (inertia).
    """
    k_values = list(range(1, 16))
    inertias =[]
    
    for k in k_values:
        # n_init='auto' to suppress warnings and run efficiently
        kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
        kmeans.fit(X)
        inertias.append(kmeans.inertia_)
        
    return k_values, inertias

def find_optimal_k(k_values, inertias):
    """
    Programmatically finds the optimal 'k' using the Elbow Method.
    It computes the maximum perpendicular distance from the curve to the 
    line connecting the first and last points.
    """
    # Normalize the axes so that the scales of K and Inertia don't distort the geometry
    k_norm = (np.array(k_values) - min(k_values)) / (max(k_values) - min(k_values))
    i_norm = (np.array(inertias) - min(inertias)) / (max(inertias) - min(inertias))
    
    p1 = np.array([k_norm[0], i_norm[0]])
    p2 = np.array([k_norm[-1], i_norm[-1]])
    
    max_dist = -1
    best_k = 1
    
    for i in range(len(k_values)):
        p = np.array([k_norm[i], i_norm[i]])
        # Calculate perpendicular distance from point p to line(p1, p2)
        dist = np.linalg.norm(np.cross(p2 - p1, p1 - p)) / np.linalg.norm(p2 - p1)
        
        if dist > max_dist:
            max_dist = dist
            best_k = k_values[i]
            
    return best_k

def plot_and_save(k_values, inertias, optimal_k):
    """
    Plots the objective value as a function of k and saves it to plot.png.
    """
    plt.figure(figsize=(8, 6))
    plt.plot(k_values, inertias, marker='o', linestyle='-', color='b', label='Objective Value')
    plt.axvline(x=optimal_k, color='r', linestyle='--', label=f'Optimal k = {optimal_k} (Elbow)')
    
    plt.title("k-means Objective Value vs. k")
    plt.xlabel("Number of clusters (k)")
    plt.ylabel("Objective Value (Sum of Squared Distances)")
    plt.xticks(k_values)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.savefig('plot.png', bbox_inches='tight')
    plt.close()

def main():
    if len(sys.argv) != 2:
        print("Usage:", file=sys.stderr)
        print("  python3 Q1.py <dataset_num>", file=sys.stderr)
        print("  python3 Q1.py <path_to_dataset>.npy", file=sys.stderr)
        sys.exit(1)
        
    arg = sys.argv[1]
    
    # 1. Load the data
    X = load_data(arg)
    
    # 2. Compute optimal solutions for k in {1...15}
    k_values, inertias = compute_kmeans(X)
    
    # 3. Determine suitable choice of k
    optimal_k = find_optimal_k(k_values, inertias)
    
    # 4. Generate the plot
    plot_and_save(k_values, inertias, optimal_k)
    
    # 5. Output exactly a single number in stdout (as required)
    print(optimal_k)

if __name__ == "__main__":
    main()