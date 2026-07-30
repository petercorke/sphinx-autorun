# Technical Debt

## `runblock` never fails the Sphinx build on a runtime error — RESOLVED

Resolved 2026-07-31 on `feature/fail-on-error`: added the opt-in
`pycon_fail_on_error` config key described below, exactly as proposed.
`runsource()`/`runblock()` (`src/sphinx_pyrunblock/interpreter.py`) now
return a structured `failed: bool` alongside each result instead of the
old marker-string sniffing, and `RunBlock.run()` raises `RunBlockError`
(with the `file:line` location, matching the existing `!! [RUNBLOCK-ERROR]`
marker's location) when enabled and any statement in the block — including
`runfirst` setup code — failed. Defaults to `False`, so existing docs with
a runblock deliberately demonstrating an error keep building unchanged.
Documented in `docs/source/{index,configuration}.rst`. Downstream
toolboxes (RTB, MVTB, SMTB, bdsim, spatialgeometry) still need to opt in
via their own `conf.py` — that rollout hasn't happened yet.

### Background

`RunBlock.run()` (`src/sphinx_pyrunblock/directive.py`) calls
`runblock()` (`src/sphinx_pyrunblock/interpreter.py`), which executes
each line of a `.. runblock:: pycon` block through an
`InteractiveInterpreter`. When the executed code raises (e.g. a missing
optional dependency), `runsource()` catches it, formats a
`!! [RUNBLOCK-ERROR] ...` marker plus indented traceback, and returns
that as the directive's *output* — but `RunBlock.run()` always returns a
`literal_block` node regardless of whether the code succeeded, so Sphinx
reports the build as green either way. `RunBlockError`
(`src/sphinx_pyrunblock/config.py`) already exists as a `SphinxError`
subclass but is never actually raised anywhere.

Concrete case that motivated this: spatialgeometry
(jhavl/spatialgeometry) has an `intro.rst` `runblock` example calling
`closest_point()`, which needs the optional `coal` dependency. The
docs-build CI job only installed the `docs` extra, not `collision`, so
the block raised `ModuleNotFoundError` on every single build — and that
traceback got baked straight into the published HTML instead of failing
CI. Nobody noticed until someone actually read the live docs page
(2026-07-28). Fixed on the spatialgeometry side by installing the right
extra, but the underlying gap in sphinx-autorun — that this class of bug
is invisible to CI — remains.

### Proposed fix

Add an opt-in `conf.py` config value, e.g. `autorun_fail_on_error = True`
(or per-language, `autorun_languages['pycon_fail_on_error'] = True`),
checked in `RunBlock.run()` after collecting `results` from `runblock()`:
if any result's output starts with the `!! [RUNBLOCK-ERROR]` marker,
raise `RunBlockError` instead of returning the `literal_block`. Default
to `False` for backward compatibility, in case any existing docs have a
runblock that's deliberately demonstrating an error/traceback as
expected output.

Once added, downstream docs builds (RTB, MVTB, SMTB, bdsim,
spatialgeometry) should opt in — turns today's "silently ships a broken
example to production docs" failure mode into a normal, visible CI
failure at the PR that introduced it.

### Resolved — package identity/publishing confusion

This used to be an open question: this repo's `pyproject.toml` was at
`0.8.0` while PyPI's published `sphinx-autorun` was at `2.0.0` under a
different, unrelated author (Hugo Osvaldo Barrera / `WhyNotHugo`) — every
toolbox's `docs` extra listed `"sphinx-autorun"` unpinned, and there was
no way to be sure a fix landed here would ever reach any of them.

Resolved 2026-07-29: this project renamed to **`sphinx-pyrunblock`** and
published properly to PyPI under that name (`pip install
sphinx-pyrunblock`, `github.com/petercorke/sphinx-pyrunblock`, hard fork,
no relation to the `sphinx-autorun` PyPI project). Downstream toolboxes
still need to switch their `docs` extra and `conf.py` `extensions` entry
from `sphinx_autorun` to `sphinx_pyrunblock` — that per-toolbox rollout
(RTB, MVTB, SMTB, spatialgeometry, swift) hasn't happened yet, but the
identity/publishing ambiguity itself is gone.
