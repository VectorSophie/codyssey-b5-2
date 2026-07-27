"""REPL for mini-git: parses input, dispatches to the Repository, prints results."""

import shlex

from .graph import ancestors as compute_ancestors
from .graph import shortest_path, topological_order
from .repo import Repository, RepoError
from .sorting import merge_sort

PROMPT = "mini-git> "


def format_commit_line(commit):
    return f"commit {commit.hash} ({commit.author}, {commit.timestamp})\n{commit.message}"


def _run_log(repo, args):
    sort_by = None
    for arg in args:
        if arg.startswith("--sort-by="):
            sort_by = arg.split("=", 1)[1]
        else:
            return "Invalid args"
    if sort_by not in (None, "date", "author"):
        return "Invalid args"

    if sort_by is None:
        commits = [repo.commits[h] for h in topological_order(repo.commits)]
    elif sort_by == "date":
        commits = merge_sort(list(repo.commits.values()), key=lambda c: c.timestamp)
    else:
        commits = merge_sort(list(repo.commits.values()), key=lambda c: c.author)

    if not commits:
        return "No commits yet."
    return "\n".join(format_commit_line(c) for c in commits)


def _run_search(repo, args):
    if len(args) != 1:
        return "Invalid args"
    arg = args[0]
    if arg.startswith("--author="):
        hashes = repo.index.search_author(arg.split("=", 1)[1])
    else:
        hashes = repo.index.search_keyword(arg)

    if not hashes:
        return "Found 0 commits."
    lines = [f"- {h}: {repo.commits[h].message}" for h in hashes]
    return f"Found {len(hashes)} commit(s):\n\n" + "\n".join(lines)


def dispatch(repo, tokens):
    if not tokens:
        return ""
    cmd = tokens[0].upper()
    args = tokens[1:]

    if cmd == "INIT":
        if len(args) != 1:
            return "Invalid args"
        repo.init(args[0])
        return (
            f"Initialized repository.\n"
            f"Current branch: {repo.current_branch}\n"
            f"Current user: {repo.current_user}"
        )

    if cmd == "BRANCH":
        if len(args) != 1:
            return "Invalid args"
        repo.branch(args[0])
        return f"Created branch: {args[0]}"

    if cmd == "SWITCH":
        if len(args) != 1:
            return "Invalid args"
        repo.switch(args[0])
        return f"Switched to branch: {args[0]}"

    if cmd == "COMMIT":
        if len(args) != 1:
            return "Invalid args"
        c = repo.commit(args[0])
        return f"[{repo.current_branch} {c.hash}] {c.message}"

    if cmd == "LOG":
        return _run_log(repo, args)

    if cmd == "PATH":
        if len(args) != 2:
            return "Invalid args"
        repo.get_commit(args[0])
        repo.get_commit(args[1])
        path = shortest_path(repo.commits, args[0], args[1])
        return "Path: " + " -> ".join(path) if path else "No path"

    if cmd == "ANCESTORS":
        if len(args) != 1:
            return "Invalid args"
        repo.get_commit(args[0])
        found = compute_ancestors(repo.commits, args[0])
        if not found:
            return f"No ancestors for {args[0]}."
        ordered = merge_sort(list(found), key=lambda h: repo.commits[h].order)
        lines = [f"- {h}: {repo.commits[h].message}" for h in ordered]
        return f"Ancestors of {args[0]}:\n" + "\n".join(lines)

    if cmd == "SEARCH":
        return _run_search(repo, args)

    return f"Unknown command: {tokens[0]}"


def main():
    repo = Repository()
    while True:
        try:
            line = input(PROMPT)
        except EOFError:
            break
        line = line.strip()
        if not line:
            continue
        if line.lower() in ("exit", "quit"):
            break
        try:
            tokens = shlex.split(line)
        except ValueError:
            print("Invalid args")
            continue
        try:
            result = dispatch(repo, tokens)
        except RepoError as exc:
            result = str(exc)
        if result:
            print(result)


if __name__ == "__main__":
    main()
