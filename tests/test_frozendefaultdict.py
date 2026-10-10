from __future__ import annotations

import copy
import pickle
import tempfile
from pathlib import Path

import pytest

from frozendefaultdict.frozendefaultdict import (
    NoDefaultValueProvidedError,
    frozendefaultdict,
)


class TestConstruction:
    """Tests relating to the construction of a FrozenDefaultDict."""

    def test_empty(self):
        fdd = frozendefaultdict()
        assert len(fdd) == 0
        assert list(fdd) == []
        assert not fdd.has_default_value

    def test_empty_explicit(self):
        fdd = frozendefaultdict(None)
        assert len(fdd) == 0
        assert list(fdd) == []
        assert not fdd.has_default_value

    def test_from_dict(self):
        fdd = frozendefaultdict({"a": 1, "b": 2})
        assert fdd["a"] == 1
        assert fdd["b"] == 2
        assert len(fdd) == 2
        assert not fdd.has_default_value

    def test_from_iterable_of_pairs(self):
        fdd = frozendefaultdict([("x", 10), ("y", 20)])
        assert fdd["x"] == 10
        assert fdd["y"] == 20
        assert not fdd.has_default_value

    def test_with_default_value(self):
        fdd = frozendefaultdict({"a": 1}, default_value=0)
        assert fdd["a"] == 1
        assert fdd["missing"] == 0
        assert fdd.has_default_value

    def test_default_value_property(self):
        fdd = frozendefaultdict(default_value=42)
        assert fdd.has_default_value
        assert fdd.default_value == 42

    def test_no_default_value(self):
        fdd = frozendefaultdict({"a": 1})
        assert not fdd.has_default_value
        with pytest.raises(NoDefaultValueProvidedError):
            _ = fdd.default_value


class TestGetItem:
    def test_existing_key(self):
        fdd = frozendefaultdict({"k": "v"})
        assert fdd["k"] == "v"

    def test_missing_key_with_default(self):
        fdd = frozendefaultdict(default_value="default")
        assert fdd["anything"] == "default"

    def test_missing_key_without_default_raises(self):
        fdd = frozendefaultdict({"a": 1})
        msg = "nonexistent"
        with pytest.raises(KeyError, match=msg):
            fdd["nonexistent"]

    def test_missing_does_not_mutate(self):
        fdd = frozendefaultdict(default_value=0)
        _ = fdd["new_key"]
        assert "new_key" not in fdd
        assert len(fdd) == 0


class TestIteration:
    def test_iter(self):
        fdd = frozendefaultdict({"a": 1, "b": 2, "c": 3})
        assert set(fdd) == {"a", "b", "c"}

    def test_contains_existing(self):
        fdd = frozendefaultdict({"a": 1})
        assert "a" in fdd

    def test_contains_missing(self):
        fdd = frozendefaultdict({"a": 1}, default_value=0)
        assert "b" not in fdd

    def test_keys_values_items(self):
        data = {"x": 10, "y": 20}
        fdd = frozendefaultdict(data)
        assert set(fdd.keys()) == {"x", "y"}
        assert set(fdd.values()) == {10, 20}
        assert set(fdd.items()) == {("x", 10), ("y", 20)}


class TestEquality:
    def test_equal(self):
        a = frozendefaultdict({"a": 1}, default_value=0)
        b = frozendefaultdict({"a": 1}, default_value=0)
        assert a == b

    def test_not_equal_different_data(self):
        a = frozendefaultdict({"a": 1})
        b = frozendefaultdict({"a": 2})
        assert a != b

    def test_not_equal_different_default(self):
        a = frozendefaultdict({"a": 1}, default_value=0)
        b = frozendefaultdict({"a": 1}, default_value=99)
        assert a != b

    def test_not_equal_to_other_type(self):
        fdd = frozendefaultdict({"a": 1})
        assert fdd != {"a": 1}

    def test_eq_independent_of_insertion_order(self):
        a = frozendefaultdict({"a": 1, "b": 2})
        b = frozendefaultdict({"b": 2, "a": 1})
        assert a == b

    def test_hash_consistent_with_eq(self):
        a = frozendefaultdict({"a": 1, "b": 2})
        b = frozendefaultdict({"b": 2, "a": 1})
        assert a == b
        assert hash(a) == hash(b)

    def test_usable_as_dict_key(self):
        fdd = frozendefaultdict({"a": 1})
        d = {fdd: "value"}
        assert d[fdd] == "value"


class TestOr:
    def test_merge_with_dict(self):
        fdd = frozendefaultdict({"a": 1}, default_value=0)
        result = fdd | {"b": 2}
        assert result["a"] == 1
        assert result["b"] == 2
        assert result.default_value == 0

    def test_merge_or_overwrites(self):
        fdd = frozendefaultdict({"a": 1})
        result = fdd | {"a": 99}
        assert result["a"] == 99

    def test_merge_ror_overwrites(self):
        fdd = frozendefaultdict({"a": 1})
        result = {"a": 99} | fdd
        assert result["a"] == 1

    def test_merge_ror_keep_default_value(self):
        fdd = frozendefaultdict({"a": 1}, default_value=1)
        result = {"a": 99} | fdd
        assert result["a"] == 1
        assert result.has_default_value
        assert result.default_value == 1

    def test_merge_does_not_mutate_original(self):
        fdd = frozendefaultdict({"a": 1})
        _ = fdd | {"b": 2}
        assert "b" not in fdd

    def test_merge_with_frozen_default_dict(self):
        a = frozendefaultdict({"a": 1})
        b = frozendefaultdict({"b": 2})
        result = a | b
        assert result["a"] == 1
        assert result["b"] == 2

    def test_merge_with_frozen_default_dict_overwrites(self):
        a = frozendefaultdict({"a": 1})
        b = frozendefaultdict({"a": 99, "b": 2})
        result = a | b
        assert result["a"] == 99
        assert result["b"] == 2

    def test_merge_with_frozen_default_dict_overwrites_default_value(self):
        a = frozendefaultdict({"a": 1}, default_value=3)
        b = frozendefaultdict({"a": 99, "b": 2}, default_value=6)
        result = a | b
        assert result.default_value == 6
        result2 = b | a
        assert result2.default_value == 3

    def test_ior_does_not_change_self(self):
        a = frozendefaultdict({"a": 1})
        b = frozendefaultdict({"a": 99, "b": 2})
        acpy = copy.copy(a)
        a |= b
        assert a["a"] == 99
        assert a["b"] == 2
        assert acpy["a"] == 1
        assert "b" not in acpy


class TestHasDefaultValue:
    def test_has_default(self):
        fdd = frozendefaultdict(default_value=0)
        assert fdd.has_default_value

    def test_no_default(self):
        fdd = frozendefaultdict()
        assert not fdd.has_default_value


class TestCopy:
    def test_builtin_copy(self):
        fdd = frozendefaultdict({"mutable": []}, default_value=[0])
        fddc = copy.copy(fdd)
        assert fddc == fdd
        fdd["mutable"].append(1)
        assert fddc == fdd

    def test_builtin_deepcopy(self):
        fdd = frozendefaultdict({"mutable": []}, default_value=[0])
        fddc = copy.deepcopy(fdd)
        assert fddc == fdd
        fdd["mutable"].append(1)
        assert fddc != fdd


class TestMapKeys:
    def test_map_keys(self):
        fdd = frozendefaultdict({1: "a", 2: "b"}, default_value="z")
        result = fdd.map_keys(lambda k: k * 10)
        assert result[10] == "a"
        assert result[20] == "b"
        assert result.default_value == "z"
        assert 1 not in result
        assert 2 not in result

    def test_map_keys_preserves_values(self):
        fdd = frozendefaultdict({"a": 1, "b": 2})
        result = fdd.map_keys(str.upper)
        assert result["A"] == 1
        assert result["B"] == 2
        assert "a" not in result
        assert "b" not in result

    def test_map_keys_identity(self):
        fdd = frozendefaultdict({"a": 1, "b": 2})
        assert fdd.map_keys(lambda s: s) == fdd


class TestMapValues:
    def test_map_values(self):
        fdd = frozendefaultdict({"a": 1, "b": 2})
        result = fdd.map_values(lambda v: v * 2)
        assert result["a"] == 2
        assert result["b"] == 4

    def test_map_values_with_default(self):
        fdd = frozendefaultdict({"a": 1}, default_value=10)
        result = fdd.map_values(lambda v: v + 5)
        assert result["a"] == 6
        assert result.default_value == 15

    def test_map_values_without_default(self):
        fdd = frozendefaultdict({"a": 1})
        result = fdd.map_values(str)
        assert result["a"] == "1"
        assert not result.has_default_value


class TestMapKeysIfPresent:
    def test_maps_present_keys(self):
        fdd = frozendefaultdict({"a": 1, "b": 2, "c": 3})
        result = fdd.map_keys_if_present({"a": "x", "c": "z"})
        assert result["x"] == 1
        assert result["z"] == 3
        assert len(result) == 2

    def test_drops_unmapped_keys(self):
        fdd = frozendefaultdict({"a": 1, "b": 2})
        result = fdd.map_keys_if_present({"a": "x"})
        assert "b" not in result
        assert len(result) == 1

    def test_preserves_default_value(self):
        fdd = frozendefaultdict({"a": 1}, default_value=0)
        result = fdd.map_keys_if_present({"a": "x"})
        assert result.default_value == 0


class TestPickling:
    @pytest.mark.parametrize(
        "fdd",
        [
            frozendefaultdict(),
            frozendefaultdict({"a": 1}),
            frozendefaultdict({"b": 3}, default_value=9),
        ],
    )
    def test_pickling_round_trip(self, fdd: frozendefaultdict) -> None:
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "frozen_default_dict.pkl"

            with file.open("wb") as f:
                pickle.dump(fdd, f)

            with file.open("rb") as f:
                round_trip = pickle.load(f)

        assert round_trip == fdd
