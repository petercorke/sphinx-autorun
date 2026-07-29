<div align="center">
  <img src="https://github.com/petercorke/sphinx-pyrunblock/raw/main/docs/figs/pyrunblock-logo.svg" width="350">
  <br><br>

[![PyPI version](https://img.shields.io/pypi/v/sphinx-pyrunblock?style=for-the-badge&color=blue)](https://pypi.org/project/sphinx-pyrunblock/)
  [![Documentation](https://img.shields.io/badge/Docs-View_Online-blue?style=for-the-badge)](https://petercorke.github.io/sphinx-pyrunblock/)
  [![Build Status](https://img.shields.io/github/actions/workflow/status/petercorke/sphinx-pyrunblock/ci.yml?branch=main&style=for-the-badge)](https://github.com/petercorke/sphinx-pyrunblock/actions/workflows/ci.yml)
</div>

# sphinx-pyrunblock

Fast, in-process embedding of live Python code output into your Sphinx docs.
`sphinx-pyrunblock` runs each `.. runblock::` example directly in a shared
interpreter rather than spawning a subprocess per block — and it's backward
compatible with `sphinx-autorun`: same `runblock` directive, same
`autorun_languages` config shape, drop-in upgrade.

```rst
    .. runblock:: pycon

        >>> for i in range(5):
        ...    print(i)
```

Produces:

```
    >>> for i in range(5):
    ...    print(i)
    0
    1
    2
    3
    4
```

## Installation

```
    $ pip install sphinx-pyrunblock
```

Enable the extension by adding it to the `extensions` list in `conf.py`:

```python
    extensions.append("sphinx_pyrunblock")
```

See the [full documentation](https://petercorke.github.io/sphinx-pyrunblock/)
for configuration (`conf.py` options, `runfirst` setup), per-block directive
options (`:numpy:`, `:scipy:`, `:smtb:`, `:precision:`, `:include:`,
`:exclude:`), and how errors are reported during a build.

## Heritage

`sphinx-pyrunblock` began as a fork of
[sphinx-autorun](https://github.com/WhyNotHugo/sphinx-autorun) by Hugo
Osvaldo Barrera, itself descended from Vadim Gubergrits' original
`sphinxcontrib-autorun`. See the
[full history](https://petercorke.github.io/sphinx-pyrunblock/about.html)
for the complete lineage.
