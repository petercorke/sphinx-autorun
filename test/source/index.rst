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

.. runblock:: pycon

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
      >>> getunit([90, 180], 'deg', dim=3)

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


