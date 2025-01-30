# -*- coding: utf-8 -*-
"""
sphinxcontrib.autorun
~~~~~~~~~~~~~~~~~~~~~~

Run the code and insert stdout after the code block.

Global options

Add to your ``conf.py`` file::

    autorun_languages = {}
    autorun_languages['pycon_runfirst'] = '''
    lines of code to run before that included in the runblock
    this code does not appear in the output
    use it to set up formatting, for example
    import numpy as np
    np.set_printoptions(precision=4, suppress=True)
    '''

"""
import sys
import io

from code import InteractiveInterpreter
import contextlib

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.errors import SphinxError

from sphinx_autorun import version

__version__ = version.version


class RunBlockError(SphinxError):
    category = "runblock error"


# Declare the autorun extension
class AutoRun(object):
    # default parameters, can be overriden by conf.py
    config = {
        "pycon": "python ",
        "pycon_prefix_chars": 4,
        "pycon_show_source": False,
        "console": "bash",
        "console_prefix_chars": 1,
    }

    @classmethod
    def builder_init(cls, app):
        cls.config.update(app.builder.config.autorun_languages)


# this class is related to the particular directive
class RunBlock(Directive):
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        "linenos": directives.flag,
        "numpy": directives.flag,
        "scipy": directives.flag,
        "smtb": directives.flag,
    }
    print("Peter's version")

    def run(self):
        config = AutoRun.config  # dict of configurations from conf.py
        language = self.arguments[0]  # first argument of the directive
        # print(language)  # is pycon

        if language not in config:
            raise RunBlockError("Unknown language %s" % language)

        # Get configuration values for the language from conf.py
        args = config[language].split()
        prefix_chars = config.get(language + "_prefix_chars", 0)
        show_source = config.get(language + "_show_source", False)
        runfirst = config.get(language + "_runfirst", None)

        if "numpy" in self.options:
            runfirst = "import numpy as np\n" + runfirst
        if "scipy" in self.options:
            runfirst = "import scipy as sp\n" + runfirst
        if "smtb" in self.options:
            runfirst = "from spatialmath import *\n"

        # build the code block

        # first add the runfirst code which comes from the configuration file, its a newline separated
        # string without prompts.  This is not shown in the output
        code = [rf.strip() for rf in runfirst.split("\n") if len(rf.strip()) > 0]

        runfirst_len = len(code)

        # self.content is a list of lines of the code block, with prompts
        code += [line[prefix_chars:] for line in self.content]
        # print(code)
        results = runblock(code, show_source)
        # print(results)

        code_out = ""
        for inp, outp in results[
            runfirst_len:
        ]:  # for all i/o pairs after the runfirst code
            if "\n" in inp:
                # multiline input
                lines = inp.split("\n")
                code_out += (
                    "\n".join(
                        [">>> " + lines[0]] + ["... " + line for line in lines[1:]]
                    )
                    + "\n"
                )
            else:
                code_out += ">>> " + inp + "\n"
            if len(outp) > 0:
                code_out += outp + "\n"

        literal = nodes.literal_block(code_out, code_out)
        literal["language"] = language
        literal["linenos"] = "linenos" in self.options
        return [literal]


def setup(app):
    app.add_directive("runblock", RunBlock)
    app.connect("builder-inited", AutoRun.builder_init)
    app.add_config_value("autorun_languages", AutoRun.config, "env")


def runsource(self, source, filename="<input>", symbol="single"):
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
        # self.showsyntaxerror(filename, source=source)
        print(f" SYNTAX ERROR {e}")
        return False, None

    if code is None:
        # Case 2
        return True, None

    # Case 3

    # run the code and capture stdout to a string, stderr is ignored
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        # Execute a code object. When an exception occurs, showtraceback() is called to display a traceback. All exceptions are caught except SystemExit, which is allowed to propagate.
        self.runcode(code)

    # check if an exception happened
    # deprecated, changes to last_exc in 3.12
    try:
        exception = f"!! {type(sys.last_value).__name__}: {sys.last_value}"
        print(exception)
        del sys.last_value
    except AttributeError:
        # there was no exception in runcode()
        exception = None

    if exception is None:
        # no exception, get the value from stdout
        retval = f.getvalue()
    else:
        retval = exception

    return False, retval


def runblock(code, show_source):
    # print(code)
    source_lines = (line.rstrip() for line in code)
    console = InteractiveInterpreter()
    results = []

    try:
        while True:
            source = next(source_lines)

            more, retval = runsource(console, source)
            if show_source:
                print(source)
            while more:
                next_line = next(source_lines)
                if show_source:
                    print("...", next_line)
                source += "\n" + next_line
                more, retval = runsource(console, source)

            # lines of code included in the ReST file can be excluded from the final
            # documentation if they end with a comment # ignore
            if not source.endswith("# ignore"):
                if retval is None:
                    retval = "!! ^^^^^^^^ SYNTAX ERROR ^^^^^^^^"
                results.append((source.rstrip(), retval.rstrip()))
    except StopIteration:
        if more:
            # print("... ")
            more, retval = runsource(console, source + "\n")

    return results
