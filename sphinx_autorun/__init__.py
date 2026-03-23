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
from pathlib import Path
import contextlib

from code import InteractiveInterpreter

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.errors import SphinxError

try:
    from importlib.metadata import version as _get_version
    __version__ = _get_version('sphinx-autorun')
except Exception:
    __version__ = '0.0.0'


def shorter(path):
    """
    Reduce a path to the last two components

    :param path: path to shorten
    :type path: Path or str
    :return: shortened path
    :rtype: str
    """
    # this is horrible... but it works
    return str(Path(*Path(path).parts[-2:]))


def linerange(s):
    """
    Parse line number range string into a set of integers

    :param s: string of the form "start-end" or "start-"
    :type s: str
    :return: a set of integers in the specified range (inclusive)
    :rtype: set
    """
    if s is None:
        return set()

    parts = s.split("-")
    start = int(parts[0])
    if len(parts[1]) > 0:
        end = int(parts[1])
        return set(list(range(start, end + 1)))
    else:
        return set(list(range(start, 101)))


logfile = None


class RunBlockError(SphinxError):
    category = "runblock error"


# The name of the extension is autorun, sphinx_autorun
#  - declare the extension
class AutoRun(object):
    # default configuration parameters
    config = {
        "pycon": "python ",  # declare pycon a valid language
        "pycon_prefix_chars": 4,
        "pycon_show_source": False,
        "console": "bash",  # declare console a valid language
        "console_prefix_chars": 1,
    }

    @classmethod
    def builder_init(cls, app):
        # executed on a Sphinx builder-initd event
        # - update the configuration with the values from conf.py
        cls.config.update(app.builder.config.autorun_languages)


def setup(app):
    """
    Add the runblock directive to Sphinx
    """
    app.add_directive("runblock", RunBlock)  # invoked by .. runblock::
    app.connect(
        "builder-inited", AutoRun.builder_init
    )  # connect event "builder-inited" to AutoRun.builder_init
    app.add_config_value(
        "autorun_languages", AutoRun.config, "env"
    )  # declare autorun_languages, it is a dict defined in conf.py


# this class is related to the particular directive, is run once
class RunBlock(Directive):
    """
    Subclass of Directive that implements the runblock directive.

    The runblock directive is used to run a block of code and insert the output into the document::

        .. runblock:: ARGUMENT
            :OPTION: VALUE
            :OPTION: VALUE

            code block

    ARGUMENT is the language of the code block, e.g. pycon (Python console) or console (bash).
    Each language has some configuration options defined in the AutoRun class.

    """

    has_content = True  # directive has content, the lines of code
    required_arguments = 1  # one required arguent is the language
    optional_arguments = 0
    final_argument_whitespace = False

    # supported options
    #  .flag is True if present, False if not
    #  .unchanged means the option has a value
    option_spec = {
        "linenos": directives.flag,
        "include": directives.unchanged,
        "exclude": directives.unchanged,
        "numpy": directives.flag,
        "scipy": directives.flag,
        "smtb": directives.flag,
        "precision": directives.unchanged,
    }
    print("Peter's version")
    # global logfile
    # logfile = open("log.txt", "w")

    def run(self):
        """
        Format the code block

        This method is invoked on every invocation of the directive.

        - ``self.content`` is a list of lines of the code block, with prompts
        - ``self.arguments`` is a list of arguments to the directive
        - ``self.options`` is a dictionary of options to the directive
        """

        # get the language of the code block
        language = self.arguments[0]  # first argument of the directive

        # process configuration options
        config = AutoRun.config  # dict of configurations from defaults and conf.py

        if language not in config:
            raise RunBlockError("Unknown language %s" % language)

        # Get configuration values for the language from conf.py
        # - get the configuration values LANGUAGE_xxx
        # args = config[language].split()
        prefix_chars = config.get(
            language + "_prefix_chars", 0
        )  # number of prompt chars to strip
        show_source = config.get(
            language + "_show_source", False
        )  # show the source code

        # attempt to find which reST file contains the directive, useful for error messages
        note = self.state_machine.observers[0].__self__
        try:
            # print(f"NOTE {type({note.current_source})}: {note.current_source}")
            s = str(note.current_source)
            # print(f"  {type(s)}: {s}: {str(s)}")
            parts = s.split(":")
            srcfile = shorter(parts[0])
            rest = parts[1].split(" ")
            method = rest[-1]
            # print(f"  {srcfile} {method}")
        except:
            srcfile = "unknown"
            method = "unknown"
        rstfile = shorter(self.reporter.source)
        where = f" [ERR {srcfile}:{self.lineno}:{method} ({rstfile})]"

        runfirst = config.get(language + "_runfirst", None)

        include_lines = linerange(self.options.get("include", None))
        exclude_lines = linerange(self.options.get("exclude", None))

        # print(f"INCLUDE {include_lines}")
        # print(f"EXCLUDE {exclude_lines}")

        if "numpy" in self.options:
            runfirst += "import numpy as np\n" + runfirst
        if "scipy" in self.options:
            runfirst += "import scipy as sp\n" + runfirst
        if "smtb" in self.options:
            runfirst += "from spatialmath import *\n"
        if "precision" in self.options:
            runfirst += f"np.set_printoptions(precision={self.options['precision']})\n"

        # build the code block

        # first add the runfirst code which comes from the configuration file, its a newline separated
        # string without prompts.  This is not shown in the output
        code = [rf.strip() for rf in runfirst.split("\n") if len(rf.strip()) > 0]

        runfirst_len = len(code)

        # self.content is a list of lines of the code block, with prompts
        code += [line.strip()[prefix_chars:] for line in self.content]
        # print(code)
        # print(self.content)

        ######## RUN THE CODE BLOCK ##########
        results = runblock(code, show_source, where)

        # the result is a list of tuples, each tuple is a pair of input and output
        # print(results)

        code_out = ""
        for lineno, (inp, outp) in enumerate(
            results[runfirst_len:],
            start=1,
        ):  # for all i/o pairs after the runfirst code
            # check if the line is to be included or excluded
            if lineno in exclude_lines:
                continue
            if include_lines and lineno not in include_lines:
                continue

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
                # if linenos:
                #     code_out += f"{lineno+1:3d}:  "
                code_out += ">>> " + inp + "\n"
            if len(outp) > 0:
                # if linenos:
                #     code_out += f"     "
                code_out += outp + "\n"

        literal = nodes.literal_block(code_out, code_out)
        literal["language"] = language
        literal["linenos"] = "linenos" in self.options
        return [literal]


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
        # self.showsyntaxerror(filename, source=source)
        print(f" SYNTAX ERROR {e} {where}")
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
        exception = f"!! {type(sys.last_value).__name__}: {sys.last_value}" + where
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


def runblock(code, show_source, where):
    # come here for each block of code
    # print(code)
    # print("IN RUNBLOCK")
    source_lines = (line.rstrip() for line in code)
    console = InteractiveInterpreter()
    results = []

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

            # lines of code included in the ReST file can be excluded from the final
            # documentation if they end with a comment # ignore
            if not source.endswith("# ignore"):
                if retval is None:
                    retval = f"!! ^^^^^^^^ SYNTAX ERROR ^^^^^^^^"
                results.append((source.rstrip(), retval.rstrip()))
    except StopIteration:
        if more:
            # print("... ")
            more, retval = runsource(console, source + "\n", where=where)

    return results
