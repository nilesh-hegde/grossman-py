"""
grossman — Python client for econometrics teaching datasets.

A Python equivalent of the R ``grossman`` package by Alexander Torgovitsky.
Downloads datasets from https://github.com/a-torgovitsky/grossman-data
and returns them as pandas DataFrames.

**Important:** Always use the ``grossman.`` prefix — do NOT call
``from grossman import list, load``.  The package exports functions named
``list`` and ``load`` which shadow Python builtins.  This mirrors the R
package's convention of using ``grossman::list()`` and ``grossman::load()``.

Usage
-----
>>> import grossman
>>> grossman.list()                             # see available datasets
>>> df = grossman.load("psid")                  # load a dataset
>>> df = grossman.load("psid", variant="unbalanced")
>>> df = grossman.load("psid", refresh=True)    # force re-download
>>> grossman.clear_cache()                      # wipe local cache
"""

__version__ = "0.1.0"

from .core import clear_cache, list, load  # noqa: A004, F401
from .registry import DATASETS  # noqa: F401
