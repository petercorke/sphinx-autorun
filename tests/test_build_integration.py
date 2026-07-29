"""Real Sphinx builds for behaviour that's awkward to unit-test in isolation.

Drives ``sphinx.application.Sphinx`` directly rather than the
``sphinx.testing`` pytest plugin: that plugin's internal API has churned
across major Sphinx versions (e.g. ``sphinx.testing.path`` was removed in
Sphinx 7), whereas ``sphinx.application.Sphinx`` is the stable public
surface and ships with the base package already required by this project.
"""

from pathlib import Path

import pytest
from sphinx.application import Sphinx
from sphinx.errors import SphinxError

ROOTS = Path(__file__).parent / "roots"


def _build(src_dir, tmp_path):
    app = Sphinx(
        srcdir=str(src_dir),
        confdir=str(src_dir),
        outdir=str(tmp_path / "build"),
        doctreedir=str(tmp_path / "doctrees"),
        buildername="html",
    )
    app.build()
    return app


def test_basic_build_succeeds_with_no_raw_traceback(tmp_path):
    app = _build(ROOTS / "test-basic", tmp_path)
    assert app.statuscode == 0

    html = (tmp_path / "build" / "index.html").read_text("utf-8")
    assert "RUNBLOCK-ERROR" not in html
    assert "Traceback" not in html


def test_include_filters_to_requested_line_only(tmp_path):
    # Pygments tokenises *input* lines into many small spans, but an output
    # line (class "go", generic-output) is left as one plain span, so it's
    # the reliable thing to check for a specific rendered value.
    _build(ROOTS / "test-basic", tmp_path)
    html = (tmp_path / "build" / "index.html").read_text("utf-8")
    assert '<span class="go">two</span>' in html
    assert '<span class="go">one</span>' not in html
    assert '<span class="go">three</span>' not in html


def test_numpy_option_available_in_block(tmp_path):
    app = _build(ROOTS / "test-basic", tmp_path)
    assert app.statuscode == 0
    html = (tmp_path / "build" / "index.html").read_text("utf-8")
    assert '<span class="go">np.int64(6)</span>' in html


def test_unknown_language_raises_runblockerror(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "conf.py").write_text('extensions = ["sphinx_pyrunblock"]\n')
    (src / "index.rst").write_text(
        "Test\n====\n\n.. runblock:: no_such_language\n\n   >>> 1\n"
    )

    with pytest.raises(SphinxError, match="Unknown language"):
        _build(src, tmp_path)
