from code import InteractiveInterpreter

from sphinx_pyrunblock.interpreter import runblock, runsource


def _fresh_interpreter():
    return InteractiveInterpreter()


def test_runsource_simple_expression():
    console = _fresh_interpreter()
    more, retval, failed = runsource(console, "1 + 1", where="test:1")
    assert more is False
    assert retval.strip() == "2"
    assert failed is False


def test_runsource_multiline_needs_more_input():
    console = _fresh_interpreter()
    more, _, failed = runsource(console, "for i in range(1):", where="test:1")
    assert more is True
    assert failed is False


def test_runsource_shares_state_across_calls():
    console = _fresh_interpreter()
    runsource(console, "x = 21", where="test:1")
    _, retval, _ = runsource(console, "x * 2", where="test:2")
    assert retval.strip() == "42"


def test_runsource_syntax_error_reports_marker():
    console = _fresh_interpreter()
    more, retval, failed = runsource(console, "def f(:", where="test:5")
    assert more is False
    assert "!! [RUNBLOCK-ERROR] test:5" in retval
    assert "SyntaxError" in retval
    assert failed is True


def test_runsource_runtime_error_reports_marker_and_summary():
    console = _fresh_interpreter()
    _, retval, failed = runsource(console, "1 / 0", where="test:9")
    assert "!! [RUNBLOCK-ERROR] test:9" in retval
    assert "ZeroDivisionError" in retval
    assert failed is True


def test_runblock_pairs_source_with_output():
    results = runblock(["1 + 1", "2 + 2"], show_source=False, where="test")
    assert results == [("1 + 1", "2", False), ("2 + 2", "4", False)]


def test_runblock_ignore_suffix_suppresses_result():
    results = runblock(
        ["x = 1  # ignore", "x"], show_source=False, where="test"
    )
    assert results == [("x", "1", False)]


def test_runblock_multiline_compound_statement():
    results = runblock(
        ["for i in range(3):", "    print(i)", ""], show_source=False, where="test"
    )
    assert len(results) == 1
    assert results[0][1] == "0\n1\n2"
    assert results[0][2] is False


def test_runblock_marks_runtime_error_as_failed():
    results = runblock(["1 / 0"], show_source=False, where="test")
    assert len(results) == 1
    assert results[0][2] is True


def test_runblock_marks_syntax_error_as_failed():
    results = runblock(["def f(:"], show_source=False, where="test")
    assert len(results) == 1
    assert results[0][2] is True
