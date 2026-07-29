sphinx-pyrunblock
==================

.. image:: ../figs/pyrunblock-logo.svg
   :align: center
   :width: 350
   :alt: sphinx-pyrunblock

``sphinx-pyrunblock`` is a Sphinx extension that executes code from a
``runblock`` directive and inserts the real output into your documentation.
For example::

    .. runblock:: pycon

        >>> for i in range(5):
        ...    print(i)

produces:

.. runblock:: pycon

    >>> for i in range(5):
    ...    print(i)

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   configuration
   about

Installation
------------

.. code-block:: console

    $ pip install sphinx-pyrunblock

Enable the extension by adding it to the ``extensions`` list in ``conf.py``:

.. code-block:: python

    extensions = [
        "sphinx_pyrunblock",
    ]

See :doc:`configuration` for the full ``conf.py`` reference.

Worked examples
----------------

.. runblock:: pycon

   >>> from spatialmath.base import trnorm, troty
   >>> from numpy import linalg
   >>> T = troty(45, 'deg', t=[3, 4, 5])
   >>> linalg.det(T[:3,:3]) - 1 # is a valid SO(3)
   >>> T = T @ T @ T @ T @ T @ T @ T @ T @ T @ T @ T @ T @ T
   >>> linalg.det(T[:3,:3]) - 1  # not quite a valid SE(3) anymore
   >>> T = trnorm(T)
   >>> linalg.det(T[:3,:3]) - 1  # once more a valid SE(3)

.. runblock:: pycon

   >>> from spatialmath.base import qconj, qprint
   >>> q = [1, 2, 3, 4]
   >>> qprint(qconj(q))

Per-block options
------------------

Options are given on the directive itself, and apply to that one block only
(compare :doc:`configuration` for options that apply document-wide, via
``conf.py``):

``:linenos:``
    Show line numbers in the rendered code block.

``:include: start-end``
    Only render lines in the given range of the block's *output* (line
    numbers count the block's own statements, not the configured
    ``runfirst`` code, which never appears in output).

``:exclude: start-end``
    Skip lines in the given range, same numbering as ``:include:``.

``:numpy:``
    Prepend ``import numpy as np`` before the block runs.

``:scipy:``
    Prepend ``import scipy as sp`` before the block runs.

``:smtb:``
    Append ``from spatialmath import *`` before the block runs.

``:precision: N``
    Append ``np.set_printoptions(precision=N)`` before the block runs.
    Requires numpy to already be imported (via ``:numpy:`` or a configured
    ``runfirst`` -- see :doc:`configuration`).

.. runblock:: pycon
   :include:  5-10

      >>> from spatialmath.base import getunit
      >>> import numpy as np
      >>> getunit(1.5, 'rad')
      >>> getunit(90, 'deg')
      >>> getunit(90, 'deg', vector=False) # force a scalar output
      >>> getunit(1.5, 'rad', dim=0) # check argument is scalar
      >>> getunit(1.5, 'rad', dim=3) # check argument is a 3-vector
      >>> getunit([1.5], 'rad', dim=1) # check argument is a 1-vector
      >>> getunit([1.5], 'rad', dim=3) # check argument is a 3-vector
      >>> getunit(90, 'deg')
      >>> getunit([90, 180], 'deg')
      >>> getunit(np.r_[0.5, 1], 'rad')
      >>> getunit(np.r_[90, 180], 'deg')
      >>> getunit(np.r_[90, 180], 'deg', dim=2)
      >>> getunit([90, 180, 270], 'deg', dim=3)

For any construct with an indented body (``for``, ``while``, ``with``), it's
important to put a blank line on the end. That will be stripped off and
won't appear in the output.

.. runblock:: pycon
   :numpy:

   >>> from spatialmath.base import getunit
   >>> getunit(1.5, 'rad')
   >>> try:
   >>>   getunit(1.5, 'rad', dim=0)
   >>> except Exception as e:
   >>>   print(f"EXCEPTION {e}")
   >>>
   >>> for i in range(5):
   >>>    print(i)
   >>>

Lines ending with ``# ignore`` are executed but not shown in the rendered
output -- useful for setup code that would otherwise clutter the example.

Error reporting
----------------

If the code raises an exception, a diagnostic marker is written to the
Sphinx build log and a short error summary is embedded in the rendered
output:

.. code-block:: text

    >>> img.metadata('FocalLength')
    !! [RUNBLOCK-ERROR] machinevisiontoolbox/ImageIO.py:236
        KeyError: 'FocalLength'

The build log entry is more detailed:

.. code-block:: text

    !! [RUNBLOCK-ERROR] source/numpy.rst:98
        ModuleNotFoundError: No module named 'machinevisionToolbox'
        Traceback (most recent call last):
          File "<input>", line 1, in <module>
        ModuleNotFoundError: No module named 'machinevisionToolbox'

The marker line appears **before** the traceback so failures are easy to
scan in a long build log. The source location (``file:line``) refers to the
``.rst`` file, or the Python source file containing the docstring where the
``runblock`` directive lives.

A syntax error in the code block is reported the same way:

.. code-block:: text

    >>> print(("Hello, world")
    !! [RUNBLOCK-ERROR] source/api.rst:42
        SyntaxError: '(' was never closed
