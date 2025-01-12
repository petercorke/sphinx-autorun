Autorun is the name of the extension.

It supports two **languages**: `pycon` and `console`.  These are each subprocesses to which
the code block is piped, they run the code, and return output via pipe.

This fork eliminates the `console` languages and replaces the pipe and subprocess
with single threaded code.  Less flexible but nearly 10x faster.

# Sphinx 101


```
.. directivename:: arguments
    :key1: val1
    :key2: val2

    directive content
```

A directive has arguments, options and content.

The argument in this case is the language: pycon

The content is the block of code, lines of Python written with a `>>> ` prompt, which
is ignored but must be present.

The keys are called `options` and must be declared.  Those found appear in a dict.

Configuration options are given in `conf.py`

```
autorun_languages = {}
autorun_languages[
    "pycon_runfirst"
] = """
from spatialmath import SE3
SE3._color = False
import numpy as np
np.set_printoptions(precision=4, suppress=True)
from ansitable import ANSITable
ANSITable._color = False
"""
```

A dict is created whose name is a concatenation of the extension name (`autorun`) and
the argument name (`language`).


```
:role-name:`role content`
```


