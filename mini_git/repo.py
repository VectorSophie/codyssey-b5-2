"""Repository: branches, HEAD, and the commit store (hash -> Commit)."""

import hashlib
from datetime import datetime

from .commit import Commit
from .index import InvertedIndex


class RepoError(Exception):
    """Raised for invalid mini-git operations (unknown branch/commit, bad state)."""


class Repository:
    def __init__(self):
        self.commits = {}
        self.branches = {}
        self.current_branch = None
        self.current_user = None
        self.index = InvertedIndex()
        self._next_order = 0
        self.initialized = False

    def init(self, user_name):
        self.commits = {}
        self.branches = {"main": None}
        self.current_branch = "main"
        self.current_user = user_name
        self.index = InvertedIndex()
        self._next_order = 0
        self.initialized = True

    def branch(self, name):
        self._require_init()
        self.branches[name] = self.branches[self.current_branch]

    def switch(self, name):
        self._require_init()
        if name not in self.branches:
            raise RepoError(f"Unknown branch: {name}")
        self.current_branch = name

    def commit(self, message):
        self._require_init()
        parent = self.branches[self.current_branch]
        parents = [parent] if parent else []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_hash = self._new_hash(message, timestamp)
        c = Commit(commit_hash, message, self.current_user, timestamp, parents, self._next_order)
        self._next_order += 1
        self.commits[commit_hash] = c
        self.branches[self.current_branch] = commit_hash
        self.index.add(c)
        return c

    def get_commit(self, commit_hash):
        if commit_hash not in self.commits:
            raise RepoError(f"Unknown commit: {commit_hash}")
        return self.commits[commit_hash]

    def _new_hash(self, message, timestamp):
        # Counter + salt guarantees uniqueness even if two commits share
        # message/timestamp/order (salt only advances on an actual clash).
        salt = 0
        while True:
            raw = f"{self._next_order}:{salt}:{message}:{timestamp}".encode("utf-8")
            digest = hashlib.sha1(raw).hexdigest()[:6]
            if digest not in self.commits:
                return digest
            salt += 1

    def _require_init(self):
        if not self.initialized:
            raise RepoError("Repository not initialized. Run INIT <user_name> first.")
