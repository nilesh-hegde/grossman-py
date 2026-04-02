"""
Core functions for the grossman package.

Provides list() and load() to access econometrics teaching datasets
hosted at https://github.com/a-torgovitsky/grossman-data.

WARNING: This module intentionally exports functions named `list` and `load`
which shadow the Python builtins. Always use via the grossman namespace:

    import grossman
    grossman.list()
    grossman.load("psid")

Do NOT do: from grossman import list, load
"""

import json
import os
import shutil
import tempfile

import pandas as pd
import pyreadr
import requests

from .registry import DATASETS

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_BASE_URL = (
    "https://raw.githubusercontent.com"
    "/a-torgovitsky/grossman-data/main/data"
)

_CACHE_DIR = os.path.join(
    os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache")),
    "grossman",
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _ensure_cache_dir():
    """Create the cache directory if it does not exist."""
    os.makedirs(_CACHE_DIR, exist_ok=True)


def _cache_path(filename):
    """Return the full cache path for a given filename."""
    return os.path.join(_CACHE_DIR, filename)


def _resolve_filename(name, variant=None):
    """
    Build the base filename (without extension) for a dataset + variant.

    For the default variant this is just the dataset name (e.g. ``psid``).
    For a named variant it is ``{name}_{variant}`` (e.g. ``psid_unbalanced``).
    """
    if variant is not None:
        return f"{name}_{variant}"
    return name


def _download(url, dest):
    """Download *url* to local path *dest*, raising on HTTP errors."""
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    with open(dest, "wb") as f:
        f.write(response.content)


def _fetch_file(filename, ext, refresh=False):
    """
    Return the local path to a cached data file, downloading first if needed.

    Parameters
    ----------
    filename : str
        Base filename without extension (e.g. ``psid`` or ``psid_unbalanced``).
    ext : str
        File extension including the dot (e.g. ``".rds"`` or ``".json"``).
    refresh : bool
        If True, re-download even when a cached copy exists.

    Returns
    -------
    str
        Absolute path to the cached file.
    """
    _ensure_cache_dir()
    full_name = filename + ext
    local = _cache_path(full_name)

    if refresh or not os.path.exists(local):
        url = f"{_BASE_URL}/{full_name}"
        _download(url, local)

    return local


def _read_labels(filename, refresh=False):
    """
    Download and parse the JSON label file for a dataset.

    Returns a dict mapping column names to human-readable labels,
    or an empty dict if the file cannot be fetched.
    """
    try:
        path = _fetch_file(filename, ".json", refresh=refresh)
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def _attach_labels(df, labels):
    """
    Attach variable labels to a DataFrame as column-level metadata.

    Labels are stored in ``df.attrs["labels"]`` (a dict) so users can do::

        df.attrs["labels"]["income"]
        # => "Total household income in 2010 dollars"
    """
    if labels:
        df.attrs["labels"] = labels
    return df


# ---------------------------------------------------------------------------
# Public API  (intentionally shadows builtins — use via grossman.list / .load)
# ---------------------------------------------------------------------------


def list():                                               # noqa: A001
    """
    List all available datasets.

    Returns
    -------
    pandas.DataFrame
        A table with columns ``dataset``, ``description``, ``rows``, ``cols``,
        and ``variants``.

    Examples
    --------
    >>> import grossman
    >>> grossman.list()
    """
    rows = []
    for name, info in DATASETS.items():
        rows.append(
            {
                "dataset": name,
                "description": info["description"],
                "rows": info["rows"],
                "cols": info["cols"],
                "variants": ", ".join(info["variants"]) if info["variants"] else "",
            }
        )
    return pd.DataFrame(rows)


def load(name, variant=None, refresh=False):              # noqa: A001
    """
    Load a dataset and return it as a pandas DataFrame.

    Parameters
    ----------
    name : str
        Dataset identifier (e.g. ``"psid"``).  Must match a key in the
        dataset registry.
    variant : str or None
        Optional variant name (e.g. ``"unbalanced"`` for the PSID dataset).
    refresh : bool
        If True, ignore any cached files and re-download from GitHub.

    Returns
    -------
    pandas.DataFrame
        The requested dataset.  Variable labels (if available) are stored
        in ``df.attrs["labels"]``.

    Raises
    ------
    ValueError
        If *name* is not a known dataset or *variant* is not valid for
        the given dataset.

    Examples
    --------
    >>> import grossman
    >>> df = grossman.load("psid")
    >>> df_ub = grossman.load("psid", variant="unbalanced")
    >>> df = grossman.load("psid", refresh=True)   # force re-download
    """
    # ---- Validate dataset name ----
    if name not in DATASETS:
        available = ", ".join(sorted(DATASETS.keys()))
        raise ValueError(
            f"Unknown dataset '{name}'. Available datasets: {available}"
        )

    # ---- Validate variant ----
    meta = DATASETS[name]
    if variant is not None and variant not in meta["variants"]:
        if not meta["variants"]:
            raise ValueError(f"Dataset '{name}' has no variants.")
        allowed = ", ".join(meta["variants"])
        raise ValueError(
            f"Unknown variant '{variant}' for dataset '{name}'. "
            f"Available variants: {allowed}"
        )

    # ---- Build filename and fetch ----
    filename = _resolve_filename(name, variant)
    rds_path = _fetch_file(filename, ".rds", refresh=refresh)

    # ---- Read .rds into DataFrame ----
    result = pyreadr.read_r(rds_path)
    # pyreadr.read_r returns an OrderedDict; the single key is the object name
    df = next(iter(result.values()))

    # ---- Attach labels from the JSON sidecar ----
    # Labels are stored per base dataset name (not per variant)
    labels = _read_labels(name, refresh=refresh)
    _attach_labels(df, labels)

    return df


def clear_cache():
    """
    Delete all locally cached data files.

    This is equivalent to calling ``grossman.load(..., refresh=True)`` for
    every dataset, but faster since it simply removes the cache directory.
    """
    if os.path.isdir(_CACHE_DIR):
        shutil.rmtree(_CACHE_DIR)
