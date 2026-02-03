import numpy as np
import random
import argparse

def generate_plateau_dataset(item_universe, num_transactions=15000, output_file="generated_transactions.dat", seed=42):
    """
    Generates a dataset where:
    - Apriori: CONSTANT time at 10%, 25%, 50% support, sharp DROP at 90%
    - FP-Growth: Relatively constant across all thresholds
    
    Strategy - SIMPLE PLATEAU:
    1. Core items (8): ~92% support - always frequent, including at 90%
    2. Plateau block (10): ~52% support - frequent at 10%, 25%, 50%, NOT at 90%
       These items ALWAYS appear together, creating 2^10-1 = 1023 itemsets
       all with ~52% support
    3. Filler items (22): variable low support for diversity
    
    The plateau effect: same 1023 itemsets frequent at 10%, 25%, 50% -> same work
    At 90%: only core itemsets frequent (5 items, 31 itemsets) -> fast
    """
    random.seed(seed)
    np.random.seed(seed)
    
    num_items = len(item_universe)
    items = list(item_universe)
    
    n_core = 4
    n_plateau = 16  # Small enough that 2^10 = 1024 itemsets is manageable
    n_filler = num_items - n_core - n_plateau
    
    core_items = items[:n_core]
    plateau_items = items[n_core:n_core + n_plateau]
    filler_items = items[n_core + n_plateau:]
    
    transactions = []
    
    for tx_idx in range(num_transactions):
        transaction = set()
        for item in core_items:
            if random.random() < 0.92:
                transaction.add(item)
        if random.random() < 0.69:
            transaction.update(plateau_items) 
        else:
            transaction.update(random.sample(plateau_items, int(random.uniform(9,14))))  
        for i, item in enumerate(filler_items):
            prob = 0.075 - (i * 0.004)
            if random.random() < max(0.02, prob):
                transaction.add(item)
        if len(transaction) < 5:
            transaction.update(random.sample(core_items, min(4, len(core_items))))
        
        transactions.append(sorted(transaction))
    
    # Write to file
    with open(output_file, 'w') as f:
        for trans in transactions:
            f.write(" ".join(trans) + "\n")
    
    # Calculate statistics
    item_counts = {item: 0 for item in items}
    for trans in transactions:
        for item in trans:
            item_counts[item] += 1
    
    supports = {item: count / num_transactions * 100 for item, count in item_counts.items()}
    avg_len = sum(len(t) for t in transactions) / len(transactions)
    unique_trans = len(set(tuple(t) for t in transactions))
    
    print(f"Dataset generated (plateau pattern):")
    print(f"  Transactions: {num_transactions}")
    print(f"  Unique transactions: {unique_trans} ({100*unique_trans/num_transactions:.1f}%)")
    print(f"  Item universe size: {num_items}")
    print(f"  Avg transaction length: {avg_len:.2f}")
    print(f"  Output file: {output_file}")
    print()
    print(f"Item support distribution:")
    print(f"  Core ({n_core} items): {min(supports[i] for i in core_items):.1f}% - {max(supports[i] for i in core_items):.1f}%")
    if plateau_items:
        print(f"  Plateau ({n_plateau} items): {min(supports[i] for i in plateau_items):.1f}% - {max(supports[i] for i in plateau_items):.1f}%")
    if filler_items:
        print(f"  Filler ({n_filler} items): {min(supports[i] for i in filler_items):.1f}% - {max(supports[i] for i in filler_items):.1f}%")
    print()
    print(f"Expected behavior:")
    print(f"  Plateau items: 2^{n_plateau}-1 = {2**n_plateau - 1} itemsets at ~52% support")
    print(f"  10%, 25%, 50%: ~constant (same {2**n_plateau - 1} itemsets frequent)")
    print(f"  90%: only core -> sharp drop")
    
    return transactions


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate plateau dataset for Apriori vs FP-Growth"
    )

    # OPTIONAL positional arguments
    parser.add_argument(
        "items",
        type=int,
        nargs="?",
        default=30,
        help="Number of items in the universe (default: 30)"
    )
    parser.add_argument(
        "transactions",
        type=int,
        nargs="?",
        default=15000,
        help="Number of transactions (default: 15000)"
    )

    # Optional flags (unchanged)
    parser.add_argument("--output", type=str, default="generated_transactions.dat")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--item-prefix", type=str, default="")

    args = parser.parse_args()

    # Generate item universe
    item_universe = [f"{args.item_prefix}{i}" for i in range(args.items)]

    generate_plateau_dataset(
        item_universe,
        args.transactions,
        args.output,
        args.seed
    )

