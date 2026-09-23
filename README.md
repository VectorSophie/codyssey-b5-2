# b5-2 Mini Git — CLI 기반 커밋 그래프 엔진

Python 표준 라이브러리만으로 구현한 Mini Git. 커밋을 DAG로 저장하고,
직접 짠 위상 정렬 / 최단 경로 / 병합 정렬 / 역색인으로 LOG, PATH,
ANCESTORS, SEARCH를 처리한다.

## 개발 환경

| 항목 | 내용 |
|---|---|
| 언어 | Python 3.10 이상 |
| 외부 의존성 | 없음 (표준 라이브러리만 사용: `hashlib`, `datetime`, `shlex`) |
| 실행 | `python main.py` |
| 테스트 | `python test_mini_git.py` |

## 폴더 구조

```
codyssey-b5-2/
├── main.py               # 엔트리 포인트
├── test_mini_git.py       # assert 기반 자체 검증 스크립트
└── mini_git/
    ├── commit.py          # Commit 노드 (hash/message/author/timestamp/parents)
    ├── repo.py             # Repository: 브랜치/HEAD/커밋 저장소, 해시 발급
    ├── sorting.py          # 병합 정렬 (sorted()/list.sort() 대체)
    ├── graph.py             # 위상 정렬 / 최단 경로 / 조상 탐색
    ├── index.py             # 역색인 (keyword/author -> commit hash)
    └── cli.py               # REPL: 파싱 + 디스패치 + 출력
```

## 명령어

| 명령 | 설명 |
|---|---|
| `INIT <user_name>` | 저장소 초기화, `main` 브랜치 생성, 현재 사용자 설정 |
| `BRANCH <branch_name>` | 현재 HEAD를 가리키는 새 브랜치 생성 |
| `SWITCH <branch_name>` | HEAD를 지정 브랜치로 이동 |
| `COMMIT <message>` | 현재 HEAD를 부모로 하는 새 커밋 생성 (역색인 갱신 포함) |
| `LOG` / `LOG --sort-by=date\|author` | 커밋 로그 (기본: 부모가 자식보다 먼저) |
| `PATH <hash1> <hash2>` | 두 커밋 사이 최단 경로 (없으면 `No path`) |
| `ANCESTORS <hash>` | 해당 커밋의 모든 조상 |
| `SEARCH <keyword>` / `SEARCH --author=<name>` | 역색인 기반 검색 |
| `exit` / `quit` | 종료 |

명령어는 대소문자를 구분하지 않으며, 공백이 포함된 인자는 큰따옴표로 감싼다
(`commit "Add login feature"`). 내부 파싱은 표준 라이브러리 `shlex`를 사용해
따옴표 처리를 직접 재구현하지 않았다.

## 핵심 구현 노트

- **정렬**: `sorted()`/`list.sort()`를 쓰지 않고 `sorting.merge_sort()`를 직접
  구현했다. 병합 정렬은 평균/최악 모두 O(n log n)이고 안정 정렬이라, 동일
  작성자/동일 날짜 커밋이 원래 순서를 유지한다.
- **LOG 기본 순서**: `graph.topological_order()`가 Kahn 알고리즘(진입차수 기반
  BFS)으로 부모가 항상 자식보다 먼저 나오도록 정렬한다.
- **PATH**: 부모-자식 연결을 무방향 간선으로 보고 BFS로 최단 거리를 구한 뒤,
  목표 지점까지의 거리가 1 줄어드는 이웃 중 가장 작은 해시를 그리디하게
  선택해 사전순으로 가장 작은 경로를 재구성한다.
- **ANCESTORS**: 부모 포인터를 따라가는 단순 DFS (자기 자신은 제외).
- **SEARCH**: `index.InvertedIndex`가 커밋 생성 시점에 `keyword -> [hash]`,
  `author -> [hash]` 두 인덱스를 갱신해 두어, 검색 시 전체 커밋을 순회하지
  않는다.
- **커밋 해시**: `sha1(순번:salt:message:timestamp)`의 앞 6자리. 충돌 시
  salt를 증가시켜 재시도하므로 세션 내 유일성이 보장된다.

## 제약 준수

- `dict`/`set`/`list`는 허용 범위 내에서 사용했지만, **정렬은 100%
  자체 구현**이다 (`grep -rn "sorted(\|\.sort("` 로 실제 호출부 없음을
  확인할 수 있다 — `sorting.py`의 주석 문자열에만 이름이 등장한다).
- 그래프 전용 라이브러리(`networkx` 등)는 사용하지 않았다.
- 파일 내용 추적/네트워크/영속성은 요구사항대로 구현하지 않았다 (메모리 상
  동작).

## 실행 예시

```
mini-git> init "Alice"
Initialized repository.
Current branch: main
Current user: Alice

mini-git> commit "Initial commit"
[main 006077] Initial commit

mini-git> branch feature
Created branch: feature

mini-git> switch feature
Switched to branch: feature

mini-git> commit "Add login feature"
[feature c01cec] Add login feature

mini-git> switch main
Switched to branch: main

mini-git> commit "Add payment feature"
[main cf127b] Add payment feature

mini-git> log
commit 006077 (Alice, 2026-07-27 10:36:24)
Initial commit
commit c01cec (Alice, 2026-07-27 10:36:24)
Add login feature
commit cf127b (Alice, 2026-07-27 10:36:24)
Add payment feature

mini-git> path 006077 cf127b
Path: 006077 -> cf127b

mini-git> search login
Found 1 commit(s):

- c01cec: Add login feature
```

## 보너스 과제

미구현 (Diff/Merge/정렬 성능 비교는 이번 제출 범위에서 제외했다). `PATH`의
최단 경로 알고리즘은 이미 두 부모(merge commit)를 가진 다이아몬드 형태
그래프에서도 정확하게 동작하도록 짜여 있어 (`test_mini_git.py`의
`test_shortest_path_lexicographic_tiebreak` 참고), 추후 `MERGE` 명령을
추가해도 로직 변경이 필요 없다.
