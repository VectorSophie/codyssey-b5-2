"""Assert-based self-check. Run: python test_mini_git.py"""

from mini_git.commit import Commit
from mini_git.graph import ancestors, shortest_path, topological_order
from mini_git.repo import Repository
from mini_git.sorting import merge_sort


def test_merge_sort_is_correct_and_stable():
    items = [(3, "a"), (1, "x"), (1, "y"), (2, "b"), (1, "z")]
    result = merge_sort(items, key=lambda t: t[0])
    assert [t[0] for t in result] == [1, 1, 1, 2, 3]
    # stability: the three key==1 items must keep their original order
    assert [t[1] for t in result if t[0] == 1] == ["x", "y", "z"]


def test_repo_flow_and_log_order():
    repo = Repository()
    repo.init("Alice")
    root = repo.commit("Initial commit")

    repo.branch("feature")
    repo.switch("feature")
    login = repo.commit("Add login feature")

    repo.switch("main")
    payment = repo.commit("Add payment feature")

    assert repo.branches["main"] == payment.hash
    assert repo.branches["feature"] == login.hash
    assert login.parents == [root.hash]
    assert payment.parents == [root.hash]

    # parents-before-children topological order; ties broken by creation order
    order = topological_order(repo.commits)
    assert order == [root.hash, login.hash, payment.hash]

    # single author -> stable sort keeps creation order
    by_author = merge_sort(list(repo.commits.values()), key=lambda c: c.author)
    assert [c.hash for c in by_author] == [root.hash, login.hash, payment.hash]

    return repo, root, login, payment


def test_path_and_ancestors(repo, root, login, payment):
    # only path from login to payment goes through root (tree, no merges yet)
    path = shortest_path(repo.commits, login.hash, payment.hash)
    assert path == [login.hash, root.hash, payment.hash]

    assert shortest_path(repo.commits, root.hash, root.hash) == [root.hash]
    assert shortest_path(repo.commits, "nope", root.hash) is None

    assert ancestors(repo.commits, payment.hash) == {root.hash}
    assert ancestors(repo.commits, root.hash) == set()


def test_search_uses_inverted_index(repo, root, login, payment):
    assert repo.index.search_keyword("login") == [login.hash]
    assert repo.index.search_keyword("nonexistent") == []
    assert repo.index.search_author("Alice") == [root.hash, login.hash, payment.hash]


def test_shortest_path_lexicographic_tiebreak():
    # Diamond: a0 -> {b1, c1} -> d2 (two equal-length paths a0->b1->d2 and
    # a0->c1->d2). "b1" < "c1", so a0->b1->d2 must win.
    a0 = Commit("a0", "root", "Alice", "t0", [], 0)
    b1 = Commit("b1", "left", "Alice", "t1", ["a0"], 1)
    c1 = Commit("c1", "right", "Alice", "t2", ["a0"], 2)
    d2 = Commit("d2", "merge", "Alice", "t3", ["b1", "c1"], 3)
    commits = {c.hash: c for c in (a0, b1, c1, d2)}

    assert shortest_path(commits, "a0", "d2") == ["a0", "b1", "d2"]


def test_unique_hash_on_identical_inputs():
    repo = Repository()
    repo.init("Bob")
    first = repo.commit("same message")
    second = repo.commit("same message")
    assert first.hash != second.hash


if __name__ == "__main__":
    test_merge_sort_is_correct_and_stable()
    repo, root, login, payment = test_repo_flow_and_log_order()
    test_path_and_ancestors(repo, root, login, payment)
    test_search_uses_inverted_index(repo, root, login, payment)
    test_shortest_path_lexicographic_tiebreak()
    test_unique_hash_on_identical_inputs()
    print("All tests passed.")
