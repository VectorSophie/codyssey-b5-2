"""Inverted index: keyword -> commit hashes, author -> commit hashes.

Without this, SEARCH would have to scan every commit's message (O(commits))
on every call. With it, SEARCH does one dict lookup (O(matches)) because the
work of scanning each message happens once, at commit time, instead of once
per search.
"""


class InvertedIndex:
    def __init__(self):
        self.by_keyword = {}
        self.by_author = {}

    def add(self, commit):
        for token in commit.message.lower().split():
            self.by_keyword.setdefault(token, []).append(commit.hash)
        self.by_author.setdefault(commit.author, []).append(commit.hash)

    def search_keyword(self, keyword):
        return list(self.by_keyword.get(keyword.lower(), []))

    def search_author(self, author):
        return list(self.by_author.get(author, []))
