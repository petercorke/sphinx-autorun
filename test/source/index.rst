.. autorun documentation master file, created by
   sphinx-quickstart on Sun Jan 12 09:39:28 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

autorun documentation
=====================

Add your content using ``reStructuredText`` syntax. See the
`reStructuredText <https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html>`_
documentation for details.


.. toctree::
   :maxdepth: 2
   :caption: Contents:


Here's some code that will be executed and the output will be displayed in the documentation.


.. runblock:: pycon
   :numpy:

   >>> from spatialmath.base import getunit
   >>> import numpy as np
   >>> getunit(1.5, 'rad')
   >>> getunit(1.5, 'rad', dim=0)
   >>> try:
   >>>   getunit(1.5, 'rad', dim=0)
   >>> except Exception as e:
   >>>   print(f"EXCEPTION {e}")
   >>>
   >>> for i in range(4):
   >>>    print(i)
   >>>
   >>> getunit([1.5], 'rad', dim=0))  # --> ValueError
   >>> getunit(90, 'deg')
   >>> getunit([90, 180], 'deg')
   >>> getunit(np.r_[0.5, 1], 'rad') # ignore
   >>> getunit(np.r_[90, 180], 'deg')
   >>> getunit(np.r_[90, 180], 'deg', dim=2)
   >>> getunit([90, 180], 'deg', dim=3)  # --> ValueError

