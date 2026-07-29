from sphinx_pyrunblock.directive import build_runfirst


def test_no_options_passes_base_through_unchanged():
    assert build_runfirst("base\n", {}) == "base\n"


def test_numpy_option_prepends_without_duplicating_base():
    result = build_runfirst("base\n", {"numpy": None})
    assert result == "import numpy as np\nbase\n"
    # Regression: this used to be `base + "import numpy as np\n" + base`,
    # duplicating the entire base runfirst string instead of prepending.
    assert result.count("base") == 1


def test_scipy_option_prepends_without_duplicating_base():
    result = build_runfirst("base\n", {"scipy": None})
    assert result == "import scipy as sp\nbase\n"
    assert result.count("base") == 1


def test_smtb_option_appends():
    result = build_runfirst("base\n", {"smtb": None})
    assert result == "base\nfrom spatialmath import *\n"


def test_precision_option_appends():
    result = build_runfirst("base\n", {"precision": "4"})
    assert result == "base\nnp.set_printoptions(precision=4)\n"


def test_numpy_and_precision_combined_numpy_import_precedes_use():
    result = build_runfirst("", {"numpy": None, "precision": "2"})
    assert result == "import numpy as np\nnp.set_printoptions(precision=2)\n"


def test_all_options_combined():
    result = build_runfirst(
        "base\n", {"numpy": None, "scipy": None, "smtb": None, "precision": "3"}
    )
    assert result == (
        "import scipy as sp\nimport numpy as np\nbase\n"
        "from spatialmath import *\n"
        "np.set_printoptions(precision=3)\n"
    )
    assert result.count("base") == 1
