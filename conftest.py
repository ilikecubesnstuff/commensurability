"""Doctest configuration."""

from doctest import ELLIPSIS, NORMALIZE_WHITESPACE
from importlib.util import find_spec

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
