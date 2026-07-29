"""The execution engine: runs code through a shared InteractiveInterpreter."""

import contextlib
import io
import os
import sys
from code import InteractiveInterpreter


def _summarize_exception(stderr_text):
    """
    Extract a concise ``Type: message`` line from traceback output.

    :param stderr_text: traceback text from interpreter stderr
    :type stderr_text: str
    :return: summary string
    :rtype: str
    """
    if not stderr_text:
        return "RuntimeError: unknown runblock failure"

    lines = [line.strip() for line in stderr_text.splitlines() if line.strip()]
    if len(lines) == 0:
        return "RuntimeError: unknown runblock failure"

    # traceback output ends with "ExceptionType: message".
    return lines[-1]


def runsource(self, source, filename="<input>", symbol="single", where=None):
    """Compile and run some source in the interpreter.

    Arguments are as for compile_command().

    One of several things can happen:

    1) The input is incorrect; compile_command() raised an
    exception (SyntaxError or OverflowError).  A syntax traceback
    will be printed by calling the showsyntaxerror() method.

    2) The input is incomplete, and more input is required;
    compile_command() returned None.  Nothing happens.

    3) The input is complete; compile_command() returned a code
    object.  The code is executed by calling self.runcode() (which
    also handles run-time exceptions, except for SystemExit).

    The return value is True in case 2, False in the other cases (unless
    an exception is raised).  The return value can be used to
    decide whether to use sys.ps1 or sys.ps2 to prompt the next
    line.

    THIS IS A MODIFIED VERSION OF THE FUNCTION FROM THE CODE MODULE

    """
    try:
        code = self.compile(source, filename, symbol)
    except (OverflowError, SyntaxError, ValueError) as e:
        # Case 1
        header = f"!! [RUNBLOCK-ERROR] {where}"
        diag = f"{header}\n    SyntaxError: {e}"
        print(diag, file=sys.stderr)
        return False, diag

    if code is None:
        # Case 2
        return True, None

    # Case 3

    # run the code and capture stdout + stderr.
    # redirect_stdout/redirect_stderr catch Python-level writes; the os.dup2
    # trick additionally suppresses C-extension writes direct to fd 1/2.
    stdout = io.StringIO()
    stderr = io.StringIO()
    # Suppress stray stdout at all levels:
    #   - redirect_stdout patches sys.stdout (pure Python print() calls)
    #   - sys.__stdout__ patched for code that cached the real stdout object
    #   - os.dup2 suppresses writes direct to fd 1 (C extensions, etc.)
    devnull_fd = os.open(os.devnull, os.O_WRONLY)
    saved_stdout_fd = os.dup(1)
    real_dunder_stdout = sys.__stdout__
    os.dup2(devnull_fd, 1)
    sys.__stdout__ = stdout
    try:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            self.runcode(code)
    finally:
        sys.__stdout__ = real_dunder_stdout
        os.dup2(saved_stdout_fd, 1)
        os.close(saved_stdout_fd)
        os.close(devnull_fd)

    stdout_text = stdout.getvalue()
    stderr_text = stderr.getvalue()

    if len(stderr_text) > 0:
        summary = _summarize_exception(stderr_text)
        header = f"!! [RUNBLOCK-ERROR] {where}"
        indented_tb = "\n".join(
            "    " + line for line in stderr_text.rstrip().splitlines()
        )

        # Print marker first so failures are easy to scan in long Sphinx logs,
        # then cause on indented line, then full indented traceback.
        print(header, file=sys.stderr)
        print(f"    {summary}", file=sys.stderr)
        print(indented_tb, file=sys.stderr)

        # Include concise marker in rendered runblock output.
        retval = f"{header}\n    {summary}"
    else:
        retval = stdout_text

    return False, retval


def runblock(code, show_source, where):
    # come here for each block of code
    source_lines = (line.rstrip() for line in code)
    console = InteractiveInterpreter()
    results = []

    def append_result(source_text, retval_text):
        # lines of code included in the ReST file can be excluded from the final
        # documentation if they end with a comment # ignore
        if source_text.endswith("# ignore"):
            return
        if retval_text is None:
            retval_text = "!! ^^^^^^^^ SYNTAX ERROR ^^^^^^^^"
        results.append((source_text.rstrip(), retval_text.rstrip()))

    more = False
    source = ""

    try:
        while True:
            source = next(source_lines)

            more, retval = runsource(console, source, where=where)
            if show_source:
                print(source)
            while more:
                next_line = next(source_lines)
                if show_source:
                    print("...", next_line)
                source += "\n" + next_line
                more, retval = runsource(console, source, where=where)

            append_result(source, retval)
    except StopIteration:
        if more:
            # Force execution of an open compound statement at end of block and
            # preserve its output in the returned results.
            source = source + "\n"
            more, retval = runsource(console, source, where=where)
            append_result(source, retval)

    return results
