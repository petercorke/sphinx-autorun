# Technical Debt

## `runblock` never fails the Sphinx build on a runtime error

### Background

`RunBlock.run()` (`sphinx_autorun/__init__.py`) calls `runblock()`,
which executes each line of a `.. runblock:: pycon` block through an
`InteractiveInterpreter`. When the executed code raises (e.g. a missing
optional dependency), `runsource()` catches it, formats a
`!! [RUNBLOCK-ERROR] ...` marker plus indented traceback, and returns
that as the directive's *output* (lines ~371-389) — but `RunBlock.run()`
always returns a `literal_block` node regardless of whether the code
succeeded, so Sphinx reports the build as green either way.
`RunBlockError` (line 79) already exists as a `SphinxError` subclass but
is never actually raised anywhere.

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

### Open question — which package do downstream docs builds actually install?

This repo's `pyproject.toml` is at version `0.8.0`, but PyPI's published
`sphinx-autorun` is at `2.0.0`, with `homepage:
github.com/WhyNotHugo/sphinx-autorun` and no author set in its
metadata — i.e. it looks like it could still be the original third-party
project, not this fork. Every toolbox's `docs` extra just lists
`"sphinx-autorun"` unpinned, resolved from PyPI. Worth confirming
whether that name actually now resolves to this codebase (e.g. ownership
of the PyPI project was taken over and the metadata simply wasn't
updated) or to the unrelated upstream project, before assuming a fix
landed here ever reaches any toolbox's docs build.
