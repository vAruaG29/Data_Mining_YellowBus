import sys
import urllib.request
import json
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import warnings

warnings.filterwarnings("ignore")

def load_data_api(dataset_num):
    """
    Fetches the specific dataset from the API.
    """
    student_id = "cs5221138"
    url = f"http://hulk.cse.iitd.ac.in:3000/dataset?student_id={student_id}&dataset_num={dataset_num}"
    
    try:
        with urllib.request.urlopen(url) as response:
            raw_data = response.read().decode('utf-8')
            data = json.loads(raw_data)
            return np.array(data["X"])
    except Exception as e:
        print(f"Failed to fetch dataset {dataset_num} from API: {e}", file=sys.stderr)
        print("Make sure you are connected to the IIT network.", file=sys.stderr)
        sys.exit(1)

def compute_kmeans(X):
    """
    Computes k-means for k in {1..15} and records the objective value (inertia).
    """
    k_values = list(range(1, 16))
    inertias =[]
    
    for k in k_values:
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
    k_norm = (np.array(k_values) - min(k_values)) / (max(k_values) - min(k_values))
    i_norm = (np.array(inertias) - min(inertias)) / (max(inertias) - min(inertias))
    
    p1 = np.array([k_norm[0], i_norm[0]])
    p2 = np.array([k_norm[-1], i_norm[-1]])
    
    max_dist = -1
    best_k = 1
    
    for i in range(len(k_values)):
        p = np.array([k_norm[i], i_norm[i]])
        dist = np.linalg.norm(np.cross(p2 - p1, p1 - p)) / np.linalg.norm(p2 - p1)
        
        if dist > max_dist:
            max_dist = dist
            best_k = k_values[i]
            
    return best_k

def plot_and_save_single(k_values, inertias, optimal_k, file_label=""):
    """
    Plots a single objective value curve (used for Mode 2: .npy input).
    """
    plt.figure(figsize=(8, 6))
    plt.plot(k_values, inertias, marker='o', linestyle='-', color='b', label='Objective Value')
    plt.axvline(x=optimal_k, color='r', linestyle='--', label=f'Optimal k = {optimal_k} (Elbow)')
    
    title = "k-means Objective Value vs. k"
    if file_label:
        title += f" ({file_label})"
    plt.title(title)
    plt.xlabel("Number of clusters (k)")
    plt.ylabel("Objective Value (Sum of Squared Distances)")
    plt.xticks(k_values)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.savefig('plot.png', bbox_inches='tight')
    plt.close()

def plot_and_save_double(k_values, inertias1, opt_k1, inertias2, opt_k2):
    """
    Plots two subplots side-by-side in one figure (used for Mode 1: API number input).
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    axes[0].plot(k_values, inertias1, marker='o', linestyle='-', color='b', label='Objective Value')
    axes[0].axvline(x=opt_k1, color='r', linestyle='--', label=f'Optimal k = {opt_k1} (Elbow)')
    axes[0].set_title("Dataset 1: k-means Objective vs. k")
    axes[0].set_xlabel("Number of clusters (k)")
    axes[0].set_ylabel("Objective Value (Sum of Squared Distances)")
    axes[0].set_xticks(k_values)
    axes[0].legend()
    axes[0].grid(True, linestyle='--', alpha=0.7)
    
    axes[1].plot(k_values, inertias2, marker='o', linestyle='-', color='b', label='Objective Value')
    axes[1].axvline(x=opt_k2, color='r', linestyle='--', label=f'Optimal k = {opt_k2} (Elbow)')
    axes[1].set_title("Dataset 2: k-means Objective vs. k")
    axes[1].set_xlabel("Number of clusters (k)")
    axes[1].set_ylabel("Objective Value")
    axes[1].set_xticks(k_values)
    axes[1].legend()
    axes[1].grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig('plot.png', bbox_inches='tight')
    plt.close()

def main():
    if len(sys.argv) != 2:
        print("Usage:", file=sys.stderr)
        print("  python3 Q1.py <dataset_num>", file=sys.stderr)
        print("  python3 Q1.py <path_to_dataset>.npy", file=sys.stderr)
        sys.exit(1)
        
    arg = sys.argv[1]
    
    if str(arg).endswith('.npy'):
        X = np.load(arg)
        k_values, inertias = compute_kmeans(X)
        optimal_k = find_optimal_k(k_values, inertias)
        
        plot_and_save_single(k_values, inertias, optimal_k, file_label=arg)
        
        print(optimal_k)
        
    else:
        try:
            dataset_num_requested = int(arg)
        except ValueError:
            print("Invalid dataset_num. Must be 1 or 2.", file=sys.stderr)
            sys.exit(1)
            
        X1 = load_data_api(1)
        X2 = load_data_api(2)
        
        k_values, inertias1 = compute_kmeans(X1)
        k_values, inertias2 = compute_kmeans(X2)
        
        opt_k1 = find_optimal_k(k_values, inertias1)
        opt_k2 = find_optimal_k(k_values, inertias2)
        
        plot_and_save_double(k_values, inertias1, opt_k1, inertias2, opt_k2)
        
        if dataset_num_requested == 1:
            print(opt_k1)
        elif dataset_num_requested == 2:
            print(opt_k2)
        else:
            print(opt_k1)

if __name__ == "__main__":
    main()