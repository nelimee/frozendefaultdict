from __future__ import annotations

import pickle
import tempfile
from pathlib import Path

import pytest

from frozendefaultdict.frozendefaultdict import frozendefaultdict


def test_keys_values_items() -> None:
    data = {"x": 10, "y": 20}
    fdd = frozendefaultdict(data)
    assert set(fdd.keys()) == {"x", "y"}
    assert set(fdd.values()) == {10, 20}
    assert set(fdd.items()) == {("x", 10), ("y", 20)}


def test_usable_as_dict_key() -> None:
    fdd = frozendefaultdict({"a": 1})
    d = {fdd: "value"}
    assert d[fdd] == "value"


def test_merge_does_not_mutate_original() -> None:
    fdd = frozendefaultdict({"a": 1})
    _ = fdd | {"b": 2}
    assert "b" not in fdd


@pytest.mark.parametrize(
    "fdd",
    [
        frozendefaultdict(),
        frozendefaultdict({"a": 1}),
        frozendefaultdict({"b": 3}, default_value=9),
    ],
)
def test_pickling_round_trip(fdd: frozendefaultdict) -> None:
    with tempfile.TemporaryDirectory() as directory:
        file = Path(directory) / "frozen_default_dict.pkl"

        with file.open("wb") as f:
            pickle.dump(fdd, f)

        with file.open("rb") as f:
            round_trip = pickle.load(f)

    assert round_trip == fdd
