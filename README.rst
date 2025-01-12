==============
sphinx-autorun
==============

sphinx-autorun is an extension for Sphinx_ that can execute the code from a
runblock directive and attach the output of the execution to the document. 

.. _Sphinx: https://sphinx.readthedocs.io/

For example::

    .. runblock:: pycon
        
        >>> for i in range(5):
        ...    print(i)

Produces::

    >>> for i in range(5):
    ...    print(i)
    0
    1
    2
    3
    4


If the code throws an exception, this is indicated::
    
    >>> getunit([90, 180], 'deg', dim=3)
    !! ValueError: incorrect vector length: expected 3, got 2
    
A syntax error in the code will be displayed as an error message::

        >>> print(("Hello, world")
        !! ^^^^^^^^ SYNTAX ERROR ^^^^^^^^ 

Code environment
----------------

The code is executed in the current Python environment.  Initialization of the Python session prior
to executing the code block can be achieved by::

    .. runblock:: pycon
        :numpy:
        :scipy:
        :smtb:

        >>> np.array([1, 2, 3])

    where the options respectively import: numpy, scipy, and spatialmath-toolbox.

A more general solution is to add lines of code to the ``conf.py`` file::

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

Both options can be used together, in which case the code in the ``conf.py`` file is executed second.

Installation
------------

Installing via pip (recommended)::

    $ pip install sphinx-autorun

Install from source::

    $ git clone git@github.com:hobarrera/sphinx-autorun.git
    $ python setup.py install

To enable autorun add 'sphinx_autorun' to the ``extension`` list in
`conf.py`::

    extensions.append('sphinx_autorun')

The documentation is in the doc/ folder.

About this fork
---------------

sphinx-contrib/autorun was abandoned and broken for several months. Since it
did not even work, this fork was created as a continuation of it with mostly
critical fixes.

Recent changes have removed the need to spawn a subprocess for each code block, but
this means that the console option is no longer supported.
