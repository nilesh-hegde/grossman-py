"""
Tests for the grossman Python package.

These tests verify that the Python package mirrors the behaviour of the
R ``grossman`` package.  Tests are split into two groups:

  - **Offline tests** run without network access and verify package logic
    (registry completeness, input validation, caching mechanics).
  - **Online tests** require network access and actually download data from
    the grossman-data repository.  They are marked with ``@pytest.mark.online``
    so you can skip them in CI with ``pytest -m "not online"``.

Run all tests:         pytest
Run only offline:      pytest -m "not online"
Run only online:       pytest -m online
Verbose:               pytest -v
"""

import os
import shutil
import tempfile
from unittest import mock

import pandas as pd
import pytest

import grossman
from grossman.core import _CACHE_DIR, _resolve_filename
from grossman.registry import DATASETS

# ---------------------------------------------------------------------------
# Custom marker for tests that hit the network
# ---------------------------------------------------------------------------
online = pytest.mark.online


# ---------------------------------------------------------------------------
# 1. REGISTRY TESTS (offline — no network needed)
# ---------------------------------------------------------------------------

class TestRegistry:
    """Verify that the dataset registry is complete and well-formed."""

    EXPECTED_DATASETS = [
        "bureaucrats", "childpen", "cigs", "cookstove", "cps",
        "eskom", "hurricane", "kenyagrid", "kindy", "nit",
        "olyset", "pisa", "psid", "queens", "redistribution",
        "reservations", "tenncare", "thirdkid", "unions", "widows",
    ]

    def test_all_datasets_present(self):
        """Registry contains every dataset from the R package."""
        for name in self.EXPECTED_DATASETS:
            assert name in DATASETS, f"Missing dataset: {name}"

    def test_dataset_count(self):
        """Registry has exactly 20 datasets (same as R package)."""
        assert len(DATASETS) == 20

    def test_registry_fields(self):
        """Every entry has description, rows, cols, and variants."""
        for name, info in DATASETS.items():
            assert "description" in info, f"{name} missing description"
            assert "rows" in info, f"{name} missing rows"
            assert "cols" in info, f"{name} missing cols"
            assert "variants" in info, f"{name} missing variants"
            assert isinstance(info["rows"], int)
            assert isinstance(info["cols"], int)
            assert isinstance(info["variants"], list)

    def test_psid_has_unbalanced_variant(self):
        """PSID dataset should list 'unbalanced' as a variant."""
        assert "unbalanced" in DATASETS["psid"]["variants"]

    def test_tenncare_has_micro_variant(self):
        """TennCare dataset should list 'micro' as a variant."""
        assert "micro" in DATASETS["tenncare"]["variants"]

    def test_no_unexpected_variants(self):
        """Only psid and tenncare should have variants."""
        for name, info in DATASETS.items():
            if name not in ("psid", "tenncare"):
                assert info["variants"] == [], (
                    f"{name} has unexpected variants: {info['variants']}"
                )


# ---------------------------------------------------------------------------
# 2. LIST TESTS (offline)
# ---------------------------------------------------------------------------

class TestList:
    """Verify that grossman.list() returns the correct table."""

    def test_returns_dataframe(self):
        result = grossman.list()
        assert isinstance(result, pd.DataFrame)

    def test_columns(self):
        result = grossman.list()
        expected_cols = {"dataset", "description", "rows", "cols", "variants"}
        assert set(result.columns) == expected_cols

    def test_row_count(self):
        result = grossman.list()
        assert len(result) == 20

    def test_all_names_present(self):
        result = grossman.list()
        names = set(result["dataset"])
        for name in DATASETS:
            assert name in names


# ---------------------------------------------------------------------------
# 3. INPUT VALIDATION TESTS (offline)
# ---------------------------------------------------------------------------

class TestValidation:
    """Verify that grossman.load() rejects bad inputs gracefully."""

    def test_unknown_dataset_raises(self):
        with pytest.raises(ValueError, match="Unknown dataset"):
            grossman.load("nonexistent_dataset")

    def test_invalid_variant_raises(self):
        with pytest.raises(ValueError, match="Unknown variant"):
            grossman.load("psid", variant="does_not_exist")

    def test_variant_on_no_variant_dataset_raises(self):
        with pytest.raises(ValueError, match="has no variants"):
            grossman.load("cps", variant="something")


# ---------------------------------------------------------------------------
# 4. FILENAME RESOLUTION TESTS (offline)
# ---------------------------------------------------------------------------

class TestFilenameResolution:
    """Verify that filenames are built correctly for data downloads."""

    def test_base_name(self):
        assert _resolve_filename("psid") == "psid"

    def test_variant_name(self):
        assert _resolve_filename("psid", "unbalanced") == "psid_unbalanced"

    def test_tenncare_micro(self):
        assert _resolve_filename("tenncare", "micro") == "tenncare_micro"


# ---------------------------------------------------------------------------
# 5. ONLINE TESTS — actually download data and compare to R metadata
# ---------------------------------------------------------------------------

@online
class TestLoadSmallDataset:
    """
    Download a small dataset and verify its shape matches the R registry.

    Uses ``olyset`` (1078 rows, 4 cols) because it is the smallest dataset
    and fastest to download.
    """

    @pytest.fixture(autouse=True)
    def _setup_temp_cache(self, tmp_path):
        """Redirect the cache to a temp dir so tests are isolated."""
        self._orig_cache = _CACHE_DIR
        with mock.patch("grossman.core._CACHE_DIR", str(tmp_path)):
            yield

    def test_returns_dataframe(self):
        df = grossman.load("olyset")
        assert isinstance(df, pd.DataFrame)

    def test_olyset_shape(self):
        df = grossman.load("olyset")
        expected = DATASETS["olyset"]
        assert df.shape[0] == expected["rows"], (
            f"Row mismatch: got {df.shape[0]}, expected {expected['rows']}"
        )
        assert df.shape[1] == expected["cols"], (
            f"Col mismatch: got {df.shape[1]}, expected {expected['cols']}"
        )

    def test_labels_attached(self):
        """The JSON labels should be accessible via df.attrs['labels']."""
        df = grossman.load("olyset")
        labels = df.attrs.get("labels", {})
        # Labels dict should be non-empty and have one entry per column
        assert isinstance(labels, dict)
        # It's OK if some columns lack labels, but the dict should exist
        assert len(labels) > 0


@online
class TestLoadVariant:
    """Download a variant and verify it loads correctly."""

    @pytest.fixture(autouse=True)
    def _setup_temp_cache(self, tmp_path):
        with mock.patch("grossman.core._CACHE_DIR", str(tmp_path)):
            yield

    def test_psid_default(self):
        df = grossman.load("psid")
        expected = DATASETS["psid"]
        assert df.shape == (expected["rows"], expected["cols"])

    def test_psid_unbalanced(self):
        """The unbalanced variant should load without errors."""
        df = grossman.load("psid", variant="unbalanced")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0


@online
class TestCaching:
    """Verify that caching avoids redundant downloads."""

    @pytest.fixture(autouse=True)
    def _setup_temp_cache(self, tmp_path):
        self.cache = str(tmp_path)
        with mock.patch("grossman.core._CACHE_DIR", self.cache):
            yield

    def test_file_cached_after_load(self):
        grossman.load("olyset")
        cached_files = os.listdir(self.cache)
        assert "olyset.rds" in cached_files
        assert "olyset.json" in cached_files

    def test_refresh_redownloads(self):
        grossman.load("olyset")
        rds_path = os.path.join(self.cache, "olyset.rds")
        mtime_first = os.path.getmtime(rds_path)

        # Force re-download
        grossman.load("olyset", refresh=True)
        mtime_second = os.path.getmtime(rds_path)

        assert mtime_second >= mtime_first


@online
class TestClearCache:
    """Verify that clear_cache() removes the cache directory."""

    @pytest.fixture(autouse=True)
    def _setup_temp_cache(self, tmp_path):
        self.cache = str(tmp_path)
        with mock.patch("grossman.core._CACHE_DIR", self.cache):
            yield

    def test_clear_cache_removes_dir(self):
        grossman.load("olyset")
        assert os.path.isdir(self.cache)
        grossman.clear_cache()
        # After clearing, cached files should be gone
        # (the tmp_path itself may still exist but our sub-cache shouldn't)
        cached_files = os.listdir(self.cache) if os.path.isdir(self.cache) else []
        assert "olyset.rds" not in cached_files


# ---------------------------------------------------------------------------
# 6. CROSS-VALIDATION — verify ALL datasets match R registry dimensions
#    (slow — downloads every dataset; run only when you need confidence)
# ---------------------------------------------------------------------------

@online
@pytest.mark.slow
class TestAllDatasetDimensions:
    """
    Download every dataset and confirm (rows, cols) match the R registry.

    This is the strongest parity test: if it passes, the Python package
    returns the exact same data dimensions as the R package for every
    dataset.

    Run with:  pytest -m "online and slow" -v
    """

    @pytest.fixture(autouse=True)
    def _setup_temp_cache(self, tmp_path):
        with mock.patch("grossman.core._CACHE_DIR", str(tmp_path)):
            yield

    @pytest.mark.parametrize("name", sorted(DATASETS.keys()))
    def test_dimensions(self, name):
        df = grossman.load(name)
        expected = DATASETS[name]
        assert df.shape[0] == expected["rows"], (
            f"{name}: row mismatch {df.shape[0]} != {expected['rows']}"
        )
        assert df.shape[1] == expected["cols"], (
            f"{name}: col mismatch {df.shape[1]} != {expected['cols']}"
        )
