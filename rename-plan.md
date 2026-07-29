# Renovation plan: rename this project to `sphinx-runpyblock`

Written 2026-07-28 for a fresh Claude session to plan/execute against. This
file assumes no prior context from the conversation that produced it — the
background section exists so you don't have to re-derive it.

## Background

This repo (`petercorke/sphinx-autorun` on GitHub) is Peter's fork of a
Sphinx extension that executes code in a `.. runblock:: pycon` directive
and embeds the real output in the built docs. **It has never been
published to PyPI.** The name `sphinx-autorun` on PyPI belongs to a
different, still-actively-maintained project
(`github.com/WhyNotHugo/sphinx-autorun`, latest release 2.0.0, Jan 2025) —
this repo's `upstream` git remote, in fact; Peter's fork diverged from it.

Full lineage, oldest to newest, for context (not action items):
`sphinxcontrib-autorun` (Vadim Gubergrits, 2014, dead) →
`sphinxcontrib-autorun2` (David Wolever, 2014, parallel fork, dead) →
`sphinx-autorun-ng` (Hugo Osvaldo Barrera, 2017, dead) → `sphinx-autorun`
(same Barrera / `WhyNotHugo`, 2017–2025, **still actively maintained,
this is what PyPI resolves to**) → **this fork** (unpublished). A
side-branch, `sphinx-autorun-ebs` (Endre Bakken Stovner, 2018, dead), also
exists but isn't part of the direct line. `AUTHORS` in this repo lists the
whole chain.

### Why this matters practically

Every toolbox that depends on this fork for docs builds
(robotics-toolbox-python / RTB, machinevision-toolbox-python / MVTB,
spatialmath-python / SMTB, spatialgeometry, swift) declares
`"sphinx-autorun"` as a dependency somewhere, which — on its own —
resolves to the *wrong*, unrelated `WhyNotHugo` package on PyPI, silently
missing this fork's own additions (`numpy`/`scipy`/`smtb`/`precision`
options on `runblock`, a `!! [RUNBLOCK-ERROR]` diagnostic marker on
failure instead of a raw traceback, a Python 3.13 import fix).

**Verified state per repo, 2026-07-28** (grep each local checkout's
`pyproject.toml`, `docs/source/conf.py`, and CI config for
`sphinx-autorun` / `sphinx_autorun`):

| Repo | Declares dependency | `conf.py` extension | Already overrides with a git install? |
|---|---|---|---|
| robotics-toolbox-python | `pyproject.toml` docs extra | `sphinx_autorun` | **Yes** — `.github/workflows/ci.yml` runs `pip install git+https://github.com/petercorke/sphinx-autorun.git` |
| machinevision-toolbox-python | `pyproject.toml` docs extra | `sphinx_autorun` | **Yes** — `docs/requirements.txt` pins `sphinx-autorun @ git+https://github.com/petercorke/sphinx-autorun.git` |
| spatialmath-python | `pyproject.toml` docs extra | `sphinx_autorun` | **Yes** — `.github/workflows/sphinx.yml` runs `pip install git+https://github.com/petercorke/sphinx-autorun.git` |
| spatialgeometry (jhavl/spatialgeometry) | `pyproject.toml` docs extra | `sphinx_autorun` | **No** — currently silently builds docs against the wrong upstream package |
| swift (jhavl/swift) | `pyproject.toml` docs extra | `sphinx_autorun` | **No** — same problem as spatialgeometry |
| bdsim | — | — | Not applicable, no `sphinx-autorun` usage found in this repo |

RTB/MVTB/SMTB already (awkwardly) work around the name collision with an
explicit git-install step. spatialgeometry and swift do not, and are
currently building docs against the unrelated upstream package. This is
almost certainly why spatialgeometry's docs recently baked a *raw* Python
traceback into a published page instead of this fork's nicer
`!! [RUNBLOCK-ERROR]` marker (fixed for the immediate symptom — a missing
`coal` install — in `jhavl/spatialgeometry` PR #11, but the underlying
wrong-package issue there is still open).

**Why PyPI-hosted toolboxes can't just add a git URL to `pyproject.toml`:**
RTB/MVTB/SMTB/spatialgeometry are themselves published to PyPI, and
PyPI's upload validation rejects a package whose metadata contains a
direct URL reference (`name @ git+https://...`) in
`dependencies`/optional-dependencies. That's *why* the existing
workarounds live in CI config / a separate `requirements.txt` instead of
`pyproject.toml` itself.

## Decision already made — don't re-litigate this part

Rename this project to **`sphinx-runpyblock`** and publish it properly to
PyPI, rather than continuing to rely on git-URL install-time overrides
everywhere.

- Rejected alternative: a suffixed variant like `sphinx-autorun-pic`
  (initials, matching the `sphinx-autorun-ebs` precedent in this same
  lineage). Rejected because the lineage already has five confusingly
  similar names; a sixth continues the problem rather than resolving it.
- The RST directive name (`.. runblock:: pycon`) is **not** changing.
  `app.add_directive("runblock", RunBlock)` in `sphinx_autorun/__init__.py`
  stays as-is. No toolbox's actual `.rst` doc content needs to change —
  only the package/import name.
- `sphinx-runpyblock` was confirmed unclaimed on PyPI as of 2026-07-28.
- Provenance/continuity is kept via the `AUTHORS` file, the `upstream` git
  remote (already pointing at `WhyNotHugo/sphinx-autorun`), and a README
  paragraph describing the fork lineage — the PyPI name itself doesn't
  need to carry that weight.
- Once published under a unique name, the git-URL-override workaround
  disappears everywhere: `sphinx-runpyblock` becomes a normal, resolvable
  PyPI dependency, so `pyproject.toml` extras go back to listing it
  directly with no separate CI step needed.

### Claim the name early, before the rest of this work is done

PyPI has no formal "reserve a name" mechanism — the only way to claim one
is to actually publish a file under it. Since `sphinx-runpyblock` is a
generic-enough name that someone else could plausibly grab it first,
consider publishing a trivial placeholder release *now*, independent of
and before the rest of this plan: a minimal `pyproject.toml`
(`name = "sphinx-runpyblock"`, version `0.0.1`, no real code needed beyond
something importable) uploaded via `twine`. That establishes ownership
immediately; the real 1.0.0 rename/renovation content lands on top of it
later with no special process, since the account that published `0.0.1`
already owns the project. Check whether this has already been done before
starting the rest of the work below.

## Work items

### 1. This repo

- [ ] `pyproject.toml`: `name = "sphinx-runpyblock"`; bump version (1.0.0
      suggested, to signal independence from the old name — not yet
      decided, use judgement)
- [ ] Rename the importable module directory `sphinx_autorun/` →
      `sphinx_runpyblock/` (currently `sphinx_autorun/__init__.py`,
      ~435 lines, plus `version.py`)
- [ ] `sphinx_runpyblock/__init__.py` reads its own version via
      `importlib.metadata.version("sphinx-autorun")` near the top of the
      file (~line 34-39) — update that string to `"sphinx-runpyblock"`
- [ ] `README.md`: update title and install instructions
      (`pip install sphinx-runpyblock`); add a short "forked from
      sphinx-autorun (Hugo Barrera) / sphinxcontrib-autorun (Vadim
      Gubergrits)" provenance paragraph
- [ ] Rename the GitHub repo itself: `petercorke/sphinx-autorun` →
      `petercorke/sphinx-runpyblock` (GitHub auto-redirects old git
      remotes and web URLs, so this is low-risk)
- [ ] Keep the `upstream` remote (`WhyNotHugo/sphinx-autorun`) for any
      future upstream syncing
- [ ] Publish `sphinx-runpyblock` to PyPI — decide manual `twine upload`
      vs. setting up OIDC trusted publishing (spatialgeometry's
      `.github/workflows/cibuildwheel.yml` is a recent, working example
      of the latter if it seems worth the setup cost for a small package
      like this)
- [ ] `tech-debt.md` already in this repo (add an opt-in `conf.py` option,
      e.g. `autorun_fail_on_error`, so a `runblock` that raises actually
      fails the Sphinx build instead of silently embedding a traceback in
      the output) is separate, optional work — decide whether to bundle
      it into this same release or ship it afterward

### 2. Per-toolbox rollout (only after step 1 is published)

For each of robotics-toolbox-python, machinevision-toolbox-python,
spatialmath-python, spatialgeometry, swift:

- [ ] `pyproject.toml`: replace `"sphinx-autorun"` with
      `"sphinx-runpyblock"` in the relevant extra
- [ ] `docs/source/conf.py`: replace `sphinx_autorun` with
      `sphinx_runpyblock` in the `extensions` list
- [ ] Remove the now-unnecessary git-install override (RTB's `ci.yml`
      line, MVTB's `docs/requirements.txt` entry, SMTB's `sphinx.yml`
      line) now that `sphinx-runpyblock` resolves normally from PyPI
- [ ] Rebuild docs (locally or via CI) and confirm no page contains a raw
      traceback
- [ ] spatialgeometry and swift get the *fix* (they're on the wrong
      package today) as well as the rename in the same change — treat
      these two as higher priority than RTB/MVTB/SMTB, which already work
      correctly today via their existing overrides

### 3. After rollout

- [ ] Update `~/.claude/toolbox-infrastructure.md` (the "sphinx-autorun
      (live-executed doc examples)" section) to reflect the completed
      rename — that file currently documents the *problem*, written
      2026-07-28, and should be superseded once this is done
- [ ] Consider auditing RTB/MVTB/SMTB's docs-build CI jobs for the same
      "docs-build only installs the `docs` extra, not whatever extras the
      examples actually exercise" bug that was found and fixed in
      spatialgeometry (PR jhavl/spatialgeometry#11) — same class of issue,
      not yet checked elsewhere

## Open decisions for whoever picks this up

- Exact version number for the renamed package (1.0.0 suggested, not
  committed)
- Manual PyPI publish vs. trusted-publishing CI workflow
- Whether to bundle the "fail on error" tech-debt fix into this same
  release or ship it separately
- Rollout order — recommendation above is spatialgeometry + swift first
  (actually broken today), RTB/MVTB/SMTB after (lower urgency, already
  working around the problem)
