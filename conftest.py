"""Doctest configuration."""

import platform
from doctest import ELLIPSIS, NORMALIZE_WHITESPACE
from importlib.util import find_spec

import astropy.units as u
from sybil import Sybil
from sybil.parsers.markdown import PythonCodeBlockParser, SkipParser
from sybil.parsers.rest import DocTestParser

optionflags = ELLIPSIS | NORMALIZE_WHITESPACE

pytest_collect_file = Sybil(
    parsers=[
        DocTestParser(optionflags=optionflags),
        PythonCodeBlockParser(doctest_optionflags=optionflags),
        SkipParser(),
    ],
    patterns=["*.md", "*.py"],
).pytest()


# Ensure pidgey orbit integration works when parsing angles
u.add_enabled_equivalencies(u.dimensionless_angles())


collect_ignore_glob = []
try:
    import agama
except ImportError:  # TODO: enable these doctests
    collect_ignore_glob.append("docs/tessellation/usage/analysis/rotating_bar.md")
