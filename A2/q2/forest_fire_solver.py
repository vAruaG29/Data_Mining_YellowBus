#!/usr/bin/env python3
"""
Forest Fire Route Blocking Solver
Algorithm: AdvancedGreedy (DESCE with Dominator Trees) + GreedyReplace

Key components:
  - Edge-split graph construction for edge-domination analysis
  - Iterative dominator tree algorithm (Cooper-Harvey-Kennedy 2001)
  - DESCE scoring via dominator-tree subtree sizes
  - GreedyReplace using DESCE re-scoring (not naive MC)

Usage:
    python3 forest_fire_solver.py <graph> <seed_set> <output> <k> <n_random_instances> <hops>
"""

import sys
import time
import random
from collections import defaultdict, deque



def parse_graph(filepath):
    adj = defaultdict(list)
    edge_set = set()
    edge_prob = {}
    with open(filepath) as fh:
        for line in fh:
            parts = line.split()
            if len(parts) < 3:
                continue
            u, v = int(parts[0]), int(parts[1])
            p = float(parts[2])
            adj[u].append((v, p))
            edge_set.add((u, v))
            edge_prob[(u, v)] = p
    return adj, edge_set, edge_prob


def parse_seeds(filepath):
    seeds = []
    with open(filepath) as fh:
        for line in fh:
            tok = line.strip()
            if tok:
                seeds.append(int(tok))
    return seeds


def write_output(filepath, selected_edges):
    with open(filepath, "w") as fh:
        for u, v in selected_edges:
            fh.write(f"{u} {v}\n")

def prune_to_h_hop(seeds, adj, edge_set, edge_prob, h):
    visited = set(seeds)
    queue = deque((s, 0) for s in seeds)
    while queue:
        u, d = queue.popleft()
        if d >= h:
            continue
        for v, _ in adj[u]:
            if v not in visited:
                visited.add(v)
                queue.append((v, d + 1))
    new_adj = defaultdict(list)
    new_edges = set()
    new_prob = {}
    for u in visited:
        for v, p in adj[u]:
            if v in visited:
                new_adj[u].append((v, p))
                new_edges.add((u, v))
                new_prob[(u, v)] = p
    return new_adj, new_edges, new_prob, visited


def ic_sample(seeds, adj, blocked, max_hops):
    
    visited = set(seeds)
    live_edges = set()
    queue = deque((s, 0) for s in seeds)
    while queue:
        u, d = queue.popleft()
        if 0 < max_hops <= d:
            continue
        for v, p in adj[u]:
            if (u, v) in blocked:
                continue
            if random.random() < p:
                live_edges.add((u, v))
                if v not in visited:
                    visited.add(v)
                    queue.append((v, d + 1))
    return visited, live_edges


SUPERSOURCE = -1


def _dfs_postorder(adj_fwd, root, node_set):

    visited = set()
    post = []
    stack = [(root, False)]
    while stack:
        node, done = stack.pop()
        if done:
            post.append(node)
            continue
        if node in visited:
            continue
        visited.add(node)
        stack.append((node, True))
        for ch in adj_fwd.get(node, ()):
            if ch not in visited and ch in node_set:
                stack.append((ch, False))
    return post, visited


def compute_idom(adj_fwd, adj_bwd, root, node_set):

    post, dfs_vis = _dfs_postorder(adj_fwd, root, node_set)
    rpo = list(reversed(post))
    rpo_idx = {n: i for i, n in enumerate(rpo)}

    idom = {root: root}

    def intersect(a, b):
        while a != b:
            while rpo_idx.get(a, 10**9) > rpo_idx.get(b, 10**9):
                a = idom[a]
            while rpo_idx.get(b, 10**9) > rpo_idx.get(a, 10**9):
                b = idom[b]
        return a

    changed = True
    while changed:
        changed = False
        for n in rpo:
            if n == root or n not in dfs_vis:
                continue
            preds = [p for p in adj_bwd.get(n, ()) if p in idom]
            if not preds:
                continue
            new_d = preds[0]
            for p in preds[1:]:
                new_d = intersect(new_d, p)
            if idom.get(n) != new_d:
                idom[n] = new_d
                changed = True
    return idom


def desce_scoring(seeds, adj, edge_set, max_hops, num_samples, blocked, deadline):

    scores = defaultdict(float)
    seeds_set = frozenset(seeds)

    for _ in range(num_samples):
        if time.time() > deadline:
            break

        vis, live = ic_sample(seeds, adj, blocked, max_hops)
        if len(vis) <= len(seeds_set):
            continue

        fwd = defaultdict(list)
        bwd = defaultdict(list)
        split_map = {}           
        sid = -2

        for s in seeds:
            if s in vis:
                fwd[SUPERSOURCE].append(s)
                bwd[s].append(SUPERSOURCE)

        for (u, v) in live:
            split_map[sid] = (u, v)
            fwd[u].append(sid)
            bwd[sid].append(u)
            fwd[sid].append(v)
            bwd[v].append(sid)
            sid -= 1

        all_nodes = {SUPERSOURCE} | vis | set(split_map)

        idom = compute_idom(fwd, bwd, SUPERSOURCE, all_nodes)

        children = defaultdict(list)
        for n, d in idom.items():
            if n != d:
                children[d].append(n)

        sub = {}
        stack = [(SUPERSOURCE, False)]
        vis_dom = set()
        order = []
        while stack:
            n, done = stack.pop()
            if done:
                order.append(n)
                continue
            if n in vis_dom:
                continue
            vis_dom.add(n)
            stack.append((n, True))
            for c in children[n]:
                if c not in vis_dom:
                    stack.append((c, False))

        for n in order:

            sub[n] = 1 if (isinstance(n, int) and n >= 0
                           and n != SUPERSOURCE and n not in seeds_set
                           and n in vis) else 0
            for c in children[n]:
                sub[n] += sub.get(c, 0)

        for s_id, (u, v) in split_map.items():
            val = sub.get(s_id, 0)
            if val > 0 and (u, v) in edge_set:
                scores[(u, v)] += val

    return scores


def greedy_replace(seeds, adj, edge_set, max_hops, k,
                   output_path, start_time, time_limit, gr_samples):

    max_time = start_time + time_limit * 0.92
    seeds_set = set(seeds)

    p1_deadline = start_time + time_limit * 0.35
    scores0 = desce_scoring(seeds, adj, edge_set, max_hops,
                            gr_samples, frozenset(), p1_deadline)
    print(f"  [DESCE-init] scored {len(scores0)} edges")

    seed_out_edges = set()
    for s in seeds:
        for v, _ in adj.get(s, []):
            if (s, v) in edge_set:
                seed_out_edges.add((s, v))
    seed_out = sorted(seed_out_edges,
                      key=lambda e: scores0.get(e, 0), reverse=True)

    seen = set()
    selected = []
    for e in seed_out:
        if e not in seen and len(selected) < k:
            seen.add(e)
            selected.append(e)

    if len(selected) < k:
        for e, _ in sorted(scores0.items(), key=lambda x: -x[1]):
            if e not in seen and len(selected) < k:
                seen.add(e)
                selected.append(e)

    for e in edge_set:
        if len(selected) >= k:
            break
        if e not in seen:
            seen.add(e)
            selected.append(e)

    blocked = set(selected)
    write_output(output_path, selected)
    print(f"  [Phase 1] initial {len(selected)} edges selected")

    rescore_samples = max(500, gr_samples // 4)

    for step, idx in enumerate(reversed(range(len(selected)))):
        if time.time() > max_time:
            print(f"  [Phase 2] stopped at step {step+1}/{len(selected)} (time limit)")
            break

        removed = selected[idx]
        blocked.discard(removed)

        dl = min(time.time() + time_limit * 0.08, max_time)
        scores_reduced = desce_scoring(seeds, adj, edge_set, max_hops,
                                       rescore_samples, frozenset(blocked), dl)

        best_edge = None
        best_score = -1
        for e, s in scores_reduced.items():
            if e not in blocked and s > best_score:
                best_edge = e
                best_score = s

        if best_edge is None:

            blocked.add(removed)
            break

        if best_edge == removed:
            blocked.add(removed)
            print(f"  [Phase 2] converged at step {step+1}/{len(selected)} "
                  f"(edge {removed} is still the best for its slot)")
            break

        blocked.add(best_edge)
        selected[idx] = best_edge
        write_output(output_path, selected)
        print(f"  step {step+1}/{len(selected)}: "
              f"{removed} → {best_edge}  (Δ={best_score:.0f})")

    return selected


def main():
    if len(sys.argv) != 7:
        print("Usage: python3 forest_fire_solver.py "
              "<graph> <seed_set> <output> <k> <n_random_instances> <hops>")
        sys.exit(1)

    graph_file = sys.argv[1]
    seed_file  = sys.argv[2]
    output_file = sys.argv[3]
    k           = int(sys.argv[4])
    n_instances = int(sys.argv[5])
    hops        = int(sys.argv[6])

    start = time.time()
    TIME_LIMIT = 3500
    max_hops = hops if hops > 0 else -1

    random.seed(42)

    print(f"[{time.time()-start:.1f}s] Loading graph …")
    adj, edge_set, edge_prob = parse_graph(graph_file)
    seeds = parse_seeds(seed_file)
    all_nodes = set(adj.keys())
    for u in list(adj.keys()):
        for v, _ in adj[u]:
            all_nodes.add(v)
    print(f"  nodes={len(all_nodes)}  edges={len(edge_set)}  seeds={len(seeds)}")

    if hops > 0:
        print(f"[{time.time()-start:.1f}s] Pruning to {hops}-hop subgraph …")
        adj, edge_set, edge_prob, active = prune_to_h_hop(
            seeds, adj, edge_set, edge_prob, hops)
        print(f"  pruned nodes={len(active)}  edges={len(edge_set)}")

    ne = len(edge_set)
    if hops > 0 and ne < 5000:
        gr_samples = 20000
    elif ne < 20000:
        gr_samples = 10000
    else:
        gr_samples = 5000

    print(f"[{time.time()-start:.1f}s] Starting GreedyReplace …")
    selected = greedy_replace(seeds, adj, edge_set, max_hops, k,
                              output_file, start, TIME_LIMIT, gr_samples)
    print(f"[{time.time()-start:.1f}s] GreedyReplace done")

    write_output(output_file, selected)
    print(f"[{time.time()-start:.1f}s] Finished.  Output: {output_file}")


if __name__ == "__main__":
    main()
