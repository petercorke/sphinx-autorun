"""Extension-wide configuration: the AutoRun language registry and errors."""

from sphinx.errors import SphinxError


class RunBlockError(SphinxError):
    category = "runblock error"


class AutoRun(object):
    """Registry of languages a ``runblock`` directive may target.

    Populated with defaults below, then merged with the ``autorun_languages``
    dict from ``conf.py`` on the Sphinx ``builder-inited`` event.
    """

    # default configuration parameters
    config = {
        "pycon": "python ",  # declare pycon a valid language
        "pycon_prefix_chars": 4,
        "pycon_show_source": False,
        "pycon_fail_on_error": False,
    }

    @classmethod
    def builder_init(cls, app):
        # executed on a Sphinx builder-inited event
        # - update the configuration with the values from conf.py
        cls.config.update(app.builder.config.autorun_languages)
