# Move readiness — relocating this repo to an SSD

Written 2026-08-01. Every size and path below was measured in-session, not estimated.

The short version: **git history, `src/`, `tests/` and `data/reference_pack/` all move
cleanly. Four things do not.** Two of them are silent — they will not error, they will just
be wrong or gone.

## What breaks, ranked

### 1. `.venv/` — WILL BREAK. Rebuild it, do not copy it. (177 MB)

Every console script hardcodes the current absolute path in its shebang:

```
$ head -1 .venv/bin/pytest
#!/Users/mac/Documents/photography-WORKFLOW-local/04-drone-video-editing-ai/.venv/bin/python3
```

`drone-highlights`, `drone-stitch`, `pytest`, `f2py`, `otiocat` and the `activate` scripts
all carry it. After the move they point at a path that no longer exists.

`.venv/pyvenv.cfg` has `home = /Users/mac/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin`,
which lives under `$HOME` and is therefore **unaffected** by moving the project — so the
interpreter itself is fine and only the project-path shebangs are wrong.

**Do this instead of copying:** exclude `.venv/` from the move, then at the destination run
the recipe CLAUDE.md already records as working:

```bash
uv venv --python 3.12 --clear .venv && VIRTUAL_ENV=.venv uv pip install -e ".[dev]"
```

Then apply `pyproject.toml`'s documented opencv fix — installing the project pulls **both**
`opencv-python` (via `scenedetect`) and `opencv-contrib-python`, every time — and verify the
concrete factory, not just the module:

```bash
.venv/bin/python -c "import cv2; cv2.saliency.StaticSaliencySpectralResidual_create()"
```

Do **not** `--no-deps` reinstall before the project install succeeds; that strips `numpy`.
System `python3` is 3.9.6 and `pyproject.toml` requires `>=3.10`, so the venv must be built
on 3.10+ or `pip install -e .` fails with "requires a different Python".

Success check at the destination: `.venv/bin/python -m pytest -q` → **103 passed**
(93 unit + 10 integration), which is the count as of 2026-08-01.

### 2. Chat history AND the file-based memory — WILL BE ORPHANED, SILENTLY. (6.8 MB)

Claude Code stores both session transcripts and the persistent file-based memory under
`~/.claude/projects/<slug>/`, where `<slug>` is derived from the project's **absolute path**.
Moving the folder produces a new slug, so a new empty directory is created and every prior
session *and every saved memory* becomes unreachable from the new location — `/resume` will
find nothing and report no error, and the memory index will come back empty as though it had
never been written.

Note this applies to **two** slugs, because sessions have been opened at both paths:
`…-04-drone-video-editing-ai` (transcripts + `workflow-stall-cause-is-return-schema-size.md`)
and `…-04a-drone-video-highlights-ai` (this session's transcript + `wrong-repo-root.md`).

**Already handled:** all three transcripts and both memory directories have been copied into
`.claude/transcripts/` (memory under `memory-snapshot/from-<dir>/`) so they travel with the
folder. They are gitignored (see item 5), so they are durable across the move without being
published to the public remote. Originals were copied, not moved.

After the move, memory files are **not** picked up from the repo automatically — they must be
copied back into the new `~/.claude/projects/<new-slug>/memory/` to become live again. The
snapshot preserves them; it does not reinstate them.

### 3. Sibling read-only trees — BREAK IF YOU MOVE ONLY THIS FOLDER

`CLAUDE.md`, `data/reference_pack/README.md`, `data/manifests/reference_pack.json` (20
references) and every `data/reference_pack/probe/*.json` record source footage by **absolute
path** into two siblings of this repo:

| Referenced tree | Role |
|---|---|
| `../00-assets/drone-video-examples/` | the authoritative 9-entry corpus |
| `../_archive/_p-ai-drone-video/.drone_clips/` | 6 raw masters + 39 derivatives, cross-validation only (~3.3 GB) |

These are deliberate provenance records, not bugs — but they are absolute, so:

- **Moving the whole `photography-WORKFLOW-local/` tree:** relative layout survives; the
  recorded absolute paths go stale but stay internally consistent. Lowest-risk option.
- **Moving only `04-drone-video-editing-ai/`:** the siblings are left behind and every
  recorded path is wrong. If you do this, the provenance strings must be re-pointed, and
  `data/reference_pack/README.md`'s regeneration recipes will not run as written.

Also inside `_archive/` is a known dead symlink (`_p-ai-drone-video/_p-ai-drone-video` →
a nonexistent `/Users/matthewdeane/...` path). Do not let a copy tool follow it.

### 4. `04a-drone-video-highlights-ai/` — its symlink breaks unless both folders move together

The sibling `04a-drone-video-highlights-ai/` (the stray scaffold copy — empty `.git`, no
`src/`) contains one **relative** symlink:

```
00-WORKING -> ../04-drone-video-editing-ai/00-WORKING
```

Relative, so it survives if both folders move together preserving their relative positions,
and dangles otherwise. Its disposition is still undecided — see the session summary.

### 5. Large gitignored payloads — decide deliberately, they are not in git

| Path | Size | Regenerable? |
|---|---|---|
| `00-WORKING/` | **112 GB** | No. This is the real reason for the move. |
| `data/raw/` | 3.7 GB | Yes — a convenience mirror. Verified 2026-08-01 byte-identical (sha256) to `00-assets/drone-video-examples/` for all 6 corpus clips. Re-copy rather than trust as provenance. |
| `.venv/` | 177 MB | Yes — and must be, see item 1. |
| `data/output/` | 167 MB | Yes — `.gitignore` treats it as regenerable; `reel.mp4`/`.otio`/`.edl` rebuild from the pipeline. |
| `.claude/transcripts/` | 6.8 MB | No — see item 2. Must travel. |

Everything in that table is invisible to `git status`, so a "clean tree" tells you nothing
about whether they arrived.

## What is already safe

- **Git history.** `.git` moves intact; `origin` = `https://github.com/m-deane/drone-video-ai`
  stays reachable. Repo identity does not depend on local path.
- **Hooks.** `.claude/settings.json` invokes them via `${CLAUDE_PROJECT_DIR:-.}` — no absolute
  paths in `.claude/hooks/`. Verified by grep.
- **ffmpeg/ffprobe.** `/opt/homebrew/bin`, 8.1.2 — outside the project, unaffected. Still run
  `ffprobe -version` first at the destination; CLAUDE.md documents a real `dyld` breakage from
  an unrelated `brew upgrade`.
- **`data/reference_pack/`** — all measurement artifacts are tracked and move with git.

## Post-move verification, in order

```bash
ffprobe -version                                    # dyld check first
uv venv --python 3.12 --clear .venv && VIRTUAL_ENV=.venv uv pip install -e ".[dev]"
.venv/bin/python -c "import cv2; cv2.saliency.StaticSaliencySpectralResidual_create()"
.venv/bin/python -m pytest -q                       # expect: 103 passed
ls data/raw/corpus/*.mp4 | wc -l                    # expect: 8 -- see P1-T2, a partial
                                                    # mirror still reports green
git status && git log --oneline -3
```

The `data/raw/corpus` count matters: review-tests finding **P1-T2** measured that a
partially-copied mirror yields `5 passed, 5 skipped, exit 0` — green, with the entire
letterbox false-positive guard silently skipped. After a move, that is exactly the failure
mode to expect, and the test suite will not tell you.
