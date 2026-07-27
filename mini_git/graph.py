"""Graph algorithms over the commit DAG: no graph library used.

- topological_order: parents printed before children (LOG's default order).
- shortest_path: BFS over parent links treated as undirected edges, with a
  lexicographic tie-break.
- ancestors: every commit reachable by following parent pointers.
"""

from .sorting import merge_sort


def topological_order(commits_by_hash):
    """Kahn's algorithm: every parent appears before its children.

    A commit's parents must already exist at commit time, so creation order
    already happens to satisfy that invariant in this implementation. This
    function still does real in-degree tracking (rather than just returning
    creation order) so it stays correct even for DAGs where that invariant
    doesn't hold -- e.g. imported/replayed history.
    """
    children = {h: [] for h in commits_by_hash}
    indegree = {h: 0 for h in commits_by_hash}
    for h, c in commits_by_hash.items():
        for p in c.parents:
            children[p].append(h)
            indegree[h] += 1

    by_creation = merge_sort(list(commits_by_hash.values()), key=lambda c: c.order)
    ready = [c.hash for c in by_creation if indegree[c.hash] == 0]

    order = []
    i = 0
    while i < len(ready):
        h = ready[i]
        i += 1
        order.append(h)
        for child in children[h]:
            indegree[child] -= 1
            if indegree[child] == 0:
                ready.append(child)
    return order


def _undirected_adjacency(commits_by_hash):
    adjacency = {h: [] for h in commits_by_hash}
    for h, c in commits_by_hash.items():
        for p in c.parents:
            adjacency[h].append(p)
            adjacency[p].append(h)
    return adjacency


def _bfs_distances(adjacency, source):
    """Hop-distance from source to every reachable node."""
    dist = {source: 0}
    queue = [source]
    i = 0
    while i < len(queue):
        node = queue[i]
        i += 1
        for neighbor in adjacency[node]:
            if neighbor not in dist:
                dist[neighbor] = dist[node] + 1
                queue.append(neighbor)
    return dist


def shortest_path(commits_by_hash, start, end):
    """Shortest path treating parent links as undirected edges.

    Returns a list of hashes from start to end, or None if there is no path.

    Tie-break: among all shortest paths, pick the one whose
    "hash1->hash2->..." string is lexicographically smallest. Since every
    shortest path has the same number of hops, comparing the joined strings
    is equivalent to comparing hop-by-hop -- so a greedy walk that always
    steps to the smallest-hash neighbor moving strictly closer to the
    target reproduces exactly that path, in O(V+E) instead of enumerating
    every shortest path and sorting them.
    """
    if start not in commits_by_hash or end not in commits_by_hash:
        return None
    if start == end:
        return [start]

    adjacency = _undirected_adjacency(commits_by_hash)
    dist_to_end = _bfs_distances(adjacency, end)
    if start not in dist_to_end:
        return None

    path = [start]
    current = start
    while current != end:
        candidates = merge_sort(adjacency[current], key=lambda h: h)
        next_hop = None
        for neighbor in candidates:
            if dist_to_end.get(neighbor) == dist_to_end[current] - 1:
                next_hop = neighbor
                break
        current = next_hop
        path.append(current)
    return path


def ancestors(commits_by_hash, start_hash):
    """All commits reachable by following parent edges from start_hash (excludes itself).

    Returns None if start_hash is unknown, otherwise a set of hashes.
    """
    if start_hash not in commits_by_hash:
        return None
    seen = set()
    stack = list(commits_by_hash[start_hash].parents)
    while stack:
        h = stack.pop()
        if h in seen:
            continue
        seen.add(h)
        stack.extend(commits_by_hash[h].parents)
    return seen
