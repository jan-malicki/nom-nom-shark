# tests/test_w-engine_data.py

import pytest
import os
import sys
from typing import Dict, Any, Optional, List

# --- Configuration ---
# Add the project root directory to the Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from flashfreeze.core.w_engine_data import WEngineData, WEngineSubStat, WEnginePassive
from flashfreeze.core.common import Rarity, Stat, Specialty

# --- Test Data Fixtures ---

@pytest.fixture(scope="module")
def steel_cushion_dict() -> Dict[str, Any]:
    """Raw dictionary data for Steel Cushion W-Engine."""
    return {
        "specialty": "attack", # Use lowercase as in original JSON example
        "rarity": "S",
        "base_atk": "684",
        "sub_stat": {
            "stat": "CRIT Rate",
            "value": 0.24
        },
        "passive": {
            "name": "Metal Cat Claws",
            "description": "Increases Physical DMG by {physical_dmg}%. The equipper's DMG increases by {back_dmg}% when hitting the enemy from behind.",
            "values": {
                "phase_1": {"physical_dmg": 20, "back_dmg": 25},
                "phase_2": {"physical_dmg": 25, "back_dmg": 31.5},
                "phase_3": {"physical_dmg": 30, "back_dmg": 38},
                "phase_4": {"physical_dmg": 35, "back_dmg": 44},
                "phase_5": {"physical_dmg": 40, "back_dmg": 50}
            }
        }
    }

# Fixture for a valid, parsed WEngineData object
@pytest.fixture(scope="module")
def steel_cushion_obj(steel_cushion_dict) -> Optional[WEngineData]:
    """Parsed WEngineData object for Steel Cushion."""
    obj = WEngineData.from_dict("Steel Cushion", steel_cushion_dict)
    assert obj is not None, "Failed to parse steel_cushion_dict fixture"
    return obj

# Fixture for just the passive object, useful for method testing
@pytest.fixture(scope="module")
def steel_cushion_passive_obj(steel_cushion_obj) -> Optional[WEnginePassive]:
    """Parsed WEnginePassive object for Steel Cushion."""
    assert steel_cushion_obj is not None, "Dependency fixture steel_cushion_obj failed"
    return steel_cushion_obj.passive


# --- Consolidated Tests ---

def test_wenginesubstat_from_dict():
    """Test WEngineSubStat.from_dict parsing and defaults."""
    # Valid case
    data_valid = {"stat": "CRIT DMG", "value": 0.48}
    sub_stat_valid = WEngineSubStat.from_dict(data_valid)
    assert sub_stat_valid is not None
    assert isinstance(sub_stat_valid, WEngineSubStat)
    assert sub_stat_valid.stat == Stat.CRIT_DMG
    assert sub_stat_valid.value == 0.48

    # Missing value
    data_no_val = {"stat": "ATK"}
    sub_stat_no_val = WEngineSubStat.from_dict(data_no_val)
    assert sub_stat_no_val is not None
    assert sub_stat_no_val.stat == Stat.ATK
    assert sub_stat_no_val.value == 0.0 # Default

    # Missing stat
    data_no_stat = {"value": 0.3}
    sub_stat_no_stat = WEngineSubStat.from_dict(data_no_stat)
    assert sub_stat_no_stat is not None
    assert sub_stat_no_stat.stat == Stat.UNKNOWN # Default
    assert sub_stat_no_stat.value == 0.3

    # Invalid stat string
    data_inv_stat = {"stat": "Invalid Stat Name", "value": 0.5}
    sub_stat_inv_stat = WEngineSubStat.from_dict(data_inv_stat)
    assert sub_stat_inv_stat is not None
    assert sub_stat_inv_stat.stat == Stat.UNKNOWN # Parsed as UNKNOWN
    assert sub_stat_inv_stat.value == 0.5

    # Invalid value type
    data_inv_val = {"stat": "HP", "value": "not a number"}
    sub_stat_inv_val = WEngineSubStat.from_dict(data_inv_val)
    assert sub_stat_inv_val is None # Should fail parsing

    # None and Empty input
    assert WEngineSubStat.from_dict(None) is None
    sub_stat_empty = WEngineSubStat.from_dict({})
    assert sub_stat_empty is not None # Returns default object
    assert sub_stat_empty.stat == Stat.UNKNOWN
    assert sub_stat_empty.value == 0.0

def test_wenginepassive_from_dict(steel_cushion_dict):
    """Test WEnginePassive.from_dict parsing and defaults."""
    # Valid case
    passive_data = steel_cushion_dict.get("passive")
    passive_valid = WEnginePassive.from_dict(passive_data)
    assert passive_valid is not None
    assert isinstance(passive_valid, WEnginePassive)
    assert passive_valid.name == "Metal Cat Claws"
    assert "Increases Physical DMG" in passive_valid.description
    assert isinstance(passive_valid.values, dict)
    assert "phase_1" in passive_valid.values
    assert passive_valid.values["phase_1"]["physical_dmg"] == 20

    # Missing keys case
    passive_missing = WEnginePassive.from_dict({"name": "Test Passive"})
    assert passive_missing is not None
    assert passive_missing.name == "Test Passive"
    assert passive_missing.description is None
    assert passive_missing.values == {}

    # None and Empty input
    assert WEnginePassive.from_dict(None) is None
    passive_empty = WEnginePassive.from_dict({})
    assert passive_empty is not None # Returns default object
    assert passive_empty.name is None
    assert passive_empty.description is None
    assert passive_empty.values == {}

@pytest.mark.parametrize("phase, key, expected_value", [
    (1, "physical_dmg", 20),
    (5, "physical_dmg", 40),
    (1, "back_dmg", 25),
    (5, "back_dmg", 50),
    (3, "physical_dmg", 30),
    (1, "non_existent_key", None), # Key not present
    (0, "physical_dmg", None), # Invalid phase low
    (6, "physical_dmg", None), # Invalid phase high
])
def test_wenginepassive_get_passive_value(steel_cushion_passive_obj, phase, key, expected_value):
    """Test WEnginePassive.get_passive_value for various phases and keys."""
    assert steel_cushion_passive_obj is not None
    value = steel_cushion_passive_obj.get_passive_value(phase, key)
    assert value == expected_value

def test_wenginepassive_get_value_keys(steel_cushion_passive_obj):
    """Test WEnginePassive.get_value_keys returns correct keys and handles empty values."""
    # Test with valid data
    assert steel_cushion_passive_obj is not None
    keys = steel_cushion_passive_obj.get_value_keys()
    assert isinstance(keys, list)
    assert set(keys) == {"physical_dmg", "back_dmg"} # Use set for order-independent check

    # Test with empty values
    passive_no_values = WEnginePassive(name="Test", description="Desc", values={})
    keys_no_values = passive_no_values.get_value_keys()
    assert keys_no_values == []

    # Test with invalid phase_1 data (though fixture assumes valid)
    passive_bad_phase1 = WEnginePassive(name="Test", description="Desc", values={"phase_1": "not a dict"})
    keys_bad_phase1 = passive_bad_phase1.get_value_keys()
    assert keys_bad_phase1 == []


@pytest.mark.parametrize("phase, expected_desc_part_1, expected_desc_part_2", [
    (1, "by 20%", "by 25%"),
    (3, "by 30%", "by 38%"),
    (5, "by 40%", "by 50%"),
])
def test_wenginepassive_get_formatted_description(steel_cushion_passive_obj, phase, expected_desc_part_1, expected_desc_part_2):
    """Test WEnginePassive.get_formatted_description for different phases."""
    assert steel_cushion_passive_obj is not None
    formatted = steel_cushion_passive_obj.get_formatted_description(phase)
    assert isinstance(formatted, str)
    assert expected_desc_part_1 in formatted
    assert expected_desc_part_2 in formatted

def test_wenginepassive_get_formatted_description_edge_cases(steel_cushion_passive_obj):
    """Test WEnginePassive.get_formatted_description edge cases."""
    assert steel_cushion_passive_obj is not None
    original_desc = steel_cushion_passive_obj.description

    # Invalid phase
    assert steel_cushion_passive_obj.get_formatted_description(0) == original_desc
    assert steel_cushion_passive_obj.get_formatted_description(6) == original_desc

    # No description
    passive_no_desc = WEnginePassive(name="Test", values={"phase_1": {"val": 10}})
    assert passive_no_desc.get_formatted_description(1) is None

    # Missing key in values (placeholder remains)
    # Create a temporary passive object for this test
    passive_missing_key = WEnginePassive(
        name="Test",
        description="Value is {val1} and {val2}",
        values={"phase_1": {"val1": 10}} # Missing val2
    )
    formatted_missing = passive_missing_key.get_formatted_description(1)
    assert formatted_missing == "Value is 10 and {val2}" # {val2} is not replaced


def test_wenginedata_from_dict(steel_cushion_dict):
    """Test WEngineData.from_dict parsing, defaults, and edge cases."""
    # --- Test Valid Full Data ---
    name = "Steel Cushion"
    obj_valid = WEngineData.from_dict(name, steel_cushion_dict)
    assert obj_valid is not None
    assert isinstance(obj_valid, WEngineData)
    assert obj_valid.name == name
    assert obj_valid.specialty == Specialty.ATTACK # Check enum parsing
    assert obj_valid.rarity == Rarity.S
    assert obj_valid.base_atk == 684 # Check int conversion
    assert obj_valid.sub_stat is not None
    assert isinstance(obj_valid.sub_stat, WEngineSubStat)
    assert obj_valid.sub_stat.stat == Stat.CRIT_RATE
    assert obj_valid.sub_stat.value == 0.24
    assert obj_valid.passive is not None
    assert isinstance(obj_valid.passive, WEnginePassive)
    assert obj_valid.passive.name == "Metal Cat Claws"

    # --- Test Invalid Base ATK ---
    name_inv_atk = "Test Engine Invalid ATK"
    data_inv_atk = steel_cushion_dict.copy()
    data_inv_atk["base_atk"] = "not a number"
    obj_inv_atk = WEngineData.from_dict(name_inv_atk, data_inv_atk)
    assert obj_inv_atk is not None
    assert obj_inv_atk.base_atk == 0 # Defaults to 0

    # --- Test Missing Optional Keys ---
    name_missing = "Test Engine Missing Keys"
    data_missing = {"base_atk": "100"} # Only base_atk provided
    obj_missing = WEngineData.from_dict(name_missing, data_missing)
    assert obj_missing is not None
    assert obj_missing.name == name_missing
    assert obj_missing.base_atk == 100
    assert obj_missing.specialty == Specialty.UNKNOWN # Default enum
    assert obj_missing.rarity == Rarity.UNKNOWN # Default enum
    assert obj_missing.sub_stat is None
    assert obj_missing.passive is None

    # --- Test None Input ---
    assert WEngineData.from_dict("Some Name", None) is None

    # --- Test Empty Input ---
    obj_empty = WEngineData.from_dict("Some Name", {})
    assert obj_empty is not None # Returns default object
    assert obj_empty.name == "Some Name"
    assert obj_empty.specialty == Specialty.UNKNOWN
    assert obj_empty.rarity == Rarity.UNKNOWN
    assert obj_empty.base_atk == 0
    assert obj_empty.sub_stat is None
    assert obj_empty.passive is None

