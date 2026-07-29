# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------

from sphinx_pyrunblock import __version__

project = "sphinx-pyrunblock"
copyright = "2020-2026, Peter Corke"
author = "Peter Corke"
release = __version__
version = __version__

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx_pyrunblock",
    "sphinx.ext.autosectionlabel",
]
autosectionlabel_prefix_document = True

templates_path = ["_templates"]
exclude_patterns = []

# -- sphinx-pyrunblock setup --------------------------------------------------
# Python session setup shared by every runblock example on this site: turn
# off SE3/ANSITable colour codes (they don't render usefully as plain HTML
# text) and fix numpy's print precision so output is stable across builds.
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

# -- Options for HTML output -------------------------------------------------

html_theme = "alabaster"
html_static_path = ["_static"]
