About this project
====================

``sphinx-pyrunblock`` is a hard fork of `sphinx-autorun
<https://github.com/WhyNotHugo/sphinx-autorun>`_ by Hugo Osvaldo Barrera,
itself several generations descended from the original
``sphinxcontrib-autorun`` by Vadim Gubergrits. Full acknowledgement of
that lineage lives on this page; :file:`LICENCE` and :file:`AUTHORS` in
the repository root carry the legal/contributor record.

Lineage
-------

Oldest to newest, verified against this repository's own git history
where the line passes directly through it (marked *verified* below), and
from research at the time of the 2026 rename otherwise:

- **sphinxcontrib-autorun** (Vadim Gubergrits, starting 2010-03-04
  *(verified: first commit* ``1b76446``\ *)*, hosted on the old
  Bitbucket-based ``sphinx-contrib`` collection). Michael McNeil Forbes
  contributed to this original project too (*verified*: commit
  ``be1cbd3``, 2012-11-19).
- **sphinxcontrib-autorun2** (David Wolever, 2014) -- a parallel fork
  published under a new name rather than a continuation; sphinx-contrib
  forks were commonly released this way rather than via commit rights to
  the original. Not part of this project's direct line.
- **sphinx-autorun-ng** (Hugo Osvaldo Barrera, 2017) -- dropped the
  ``sphinxcontrib`` namespace, moved off Bitbucket. Released once, then
  immediately renamed.
- **sphinx-autorun** (same Hugo Osvaldo Barrera, 2017 onward, i.e.
  ``WhyNotHugo`` on GitHub *(verified: this repository's own git history
  contains Hugo's "Fork into sphinx_autorun" commit,* ``dc9c315``\ *,
  2017-01-10)* -- this is the project still actively maintained today,
  and the one the ``sphinx-autorun`` name on PyPI resolves to.
- A separate one-off side-branch, **sphinx-autorun-ebs** (Endre Bakken
  Stovner, 2018, one release), also exists but was never touched again
  and isn't part of this line.
- **sphinx-pyrunblock** (Peter Corke) -- this project. Forked from
  ``WhyNotHugo/sphinx-autorun`` 2020-10-26 *(verified: first commit*
  ``2549daa``, *"Eliminate the line buffering error"*\ *)*. The fix was
  also submitted upstream the same day, as `PR #19
  <https://github.com/WhyNotHugo/sphinx-autorun/pull/19>`_ -- it sat open
  for over four years and was eventually closed 2025-01-02 in favour of
  `PR #65 <https://github.com/WhyNotHugo/sphinx-autorun/pull/65>`_, a
  different, simpler fix for the same underlying bug submitted by another
  contributor and merged that same day.

  No further commits landed in this fork until a rewrite arrived
  2025-01-12, replacing the original subprocess-per-block execution with
  a single, shared, in-process interpreter -- the change this project's
  speed comes from. That rewrite was motivated by real docs-build time
  becoming a pain point during the push to ship Robotics Toolbox for
  Python and Machine Vision Toolbox for Python, both of which use this
  extension to execute live code examples during their own documentation
  builds.

Why a hard fork
----------------

``sphinx-autorun`` was never published to PyPI under that name from this
line of descent -- ``sphinx-autorun`` on PyPI is, and remains, Hugo
Osvaldo Barrera's actively-maintained project. Publishing this project's
own substantially rewritten execution engine under an unrelated,
already-claimed name wasn't viable, hence the rename to
``sphinx-pyrunblock`` and a clean detachment from the GitHub fork
network it started in. The directive name (``.. runblock::``) is
unchanged, and existing ``conf.py`` ``autorun_languages`` configuration
carries over -- only the package/import name differs.
