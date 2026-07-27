"""Custom sorting.

The mission bans sorted()/list.sort(). Merge sort is used everywhere a sort
is needed because it is O(n log n) in both the average AND worst case
(unlike quicksort, which degrades to O(n^2) on adversarial input), and it is
stable -- equal-key items keep their original relative order, which matters
for LOG --sort-by=author (commits by the same author should stay in the
order they were made).
"""


def merge_sort(items, key):
    """Return a new list sorted ascending by key(item). Stable. Does not mutate items."""
    if len(items) <= 1:
        return list(items)
    mid = len(items) // 2
    left = merge_sort(items[:mid], key)
    right = merge_sort(items[mid:], key)
    return _merge(left, right, key)


def _merge(left, right, key):
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        # '<=' (not '<') on the right side is what keeps the sort stable:
        # a tie always takes the left (earlier) item first.
        if key(left[i]) <= key(right[j]):
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged
