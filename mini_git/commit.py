"""Commit: one vertex of the mini-git commit DAG."""


class Commit:
    """A single commit.

    parents is a list of parent commit hashes (0+ parents -- 0 for a root
    commit, 1 for a normal commit, 2+ for a merge commit).
    order is the creation index, used to seed topological order and as a
    stable tie-breaker when sorting.
    """

    def __init__(self, commit_hash, message, author, timestamp, parents, order):
        self.hash = commit_hash
        self.message = message
        self.author = author
        self.timestamp = timestamp
        self.parents = parents
        self.order = order

    def __repr__(self):
        return f"Commit({self.hash!r}, {self.message!r})"
