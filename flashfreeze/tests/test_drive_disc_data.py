# tests/test_drive_disc_data.py

import pytest
import os
import sys
from typing import Dict, Any, Optional, List

# --- Configuration ---
# Add the project root directory to the Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from flashfreeze.core.drive_disc_data import DriveDiscSetData, DriveDiscSetBonus
from flashfreeze.core.common import Stat

# --- Test Data Fixtures ---

@pytest.fixture(scope="module")
def woodpecker_dict() -> Dict[str, Any]:
    """Raw dictionary data for Woodpecker Electro Drive Disc set."""
    return {
        "2-piece": {
            "stat": "CRIT Rate",
            "value": 0.08
        },
        "4-piece": {
            "description": "Landing a critical hit on an enemy with a Basic Attack, Dodge Counter, or EX Special Attack increases the equipper's ATK by {atk}% for {duration}s. The buff duration for different skills are calculated separately.",
            "values": {
                "atk": 9,
                "duration": 6
            }
        }
    }

@pytest.fixture(scope="module")
def polar_metal_dict() -> Dict[str, Any]:
    """Raw dictionary data for Polar Metal (different 4pc values)."""
    return {
        "2-piece": {
            "stat": "Ice DMG",
            "value": 0.1
        },
        "4-piece": {
            "description": "Increase the DMG of Basic Attack and Dash Attack by {basic_dash_dmg}%. When any squad member inflicts Freeze or Shatter, this effect increases by an additional {basic_dash_dmg}% for {duration}s.",
            "values": {
                "basic_dash_dmg": 20,
                "duration": 12
            }
        }
    }

# Fixture for a valid, parsed DriveDiscSetData object
@pytest.fixture(scope="module")
def woodpecker_obj(woodpecker_dict) -> Optional[DriveDiscSetData]:
    """Parsed DriveDiscSetData object for Woodpecker Electro."""
    obj = DriveDiscSetData.from_dict("Woodpecker Electro", woodpecker_dict)
    assert obj is not None, "Failed to parse woodpecker_dict fixture"
    return obj

# Fixture for the 2pc bonus object, useful for method testing
@pytest.fixture(scope="module")
def woodpecker_2pc_bonus_obj(woodpecker_obj) -> Optional[DriveDiscSetBonus]:
    """Parsed DriveDiscSetBonus object for Woodpecker 2pc."""
    assert woodpecker_obj is not None, "Dependency fixture woodpecker_obj failed"
    return woodpecker_obj.bonus_2pc

# Fixture for the 4pc bonus object, useful for method testing
@pytest.fixture(scope="module")
def woodpecker_4pc_bonus_obj(woodpecker_obj) -> Optional[DriveDiscSetBonus]:
    """Parsed DriveDiscSetBonus object for Woodpecker 4pc."""
    assert woodpecker_obj is not None, "Dependency fixture woodpecker_obj failed"
    return woodpecker_obj.bonus_4pc


# --- Consolidated Tests ---

def test_drivediscsetbonus_from_dict():
    """Test DriveDiscSetBonus.from_dict parsing and defaults for 2pc and 4pc."""
    # --- Test 2-Piece ---
    # Valid 2pc
    data_2pc_valid = {"stat": "ATK", "value": 0.1}
    bonus_2pc_valid = DriveDiscSetBonus.from_dict(2, data_2pc_valid)
    assert bonus_2pc_valid is not None
    assert bonus_2pc_valid.piece_count == 2
    assert bonus_2pc_valid.stat == Stat.ATK
    assert bonus_2pc_valid.value == 0.1
    assert bonus_2pc_valid.description is None
    assert bonus_2pc_valid.values == {}

    # 2pc Missing value
    data_2pc_no_val = {"stat": "Energy Regen"}
    bonus_2pc_no_val = DriveDiscSetBonus.from_dict(2, data_2pc_no_val)
    assert bonus_2pc_no_val is not None
    assert bonus_2pc_no_val.stat == Stat.ENERGY_REGEN
    assert bonus_2pc_no_val.value is None # Value is optional

    # 2pc Missing stat
    data_2pc_no_stat = {"value": 0.15}
    bonus_2pc_no_stat = DriveDiscSetBonus.from_dict(2, data_2pc_no_stat)
    assert bonus_2pc_no_stat is not None
    assert bonus_2pc_no_stat.stat == Stat.UNKNOWN # Defaults to UNKNOWN
    assert bonus_2pc_no_stat.value == 0.15

    # 2pc Invalid stat string
    data_2pc_inv_stat = {"stat": "Invalid", "value": 0.1}
    bonus_2pc_inv_stat = DriveDiscSetBonus.from_dict(2, data_2pc_inv_stat)
    assert bonus_2pc_inv_stat is not None
    assert bonus_2pc_inv_stat.stat == Stat.UNKNOWN # Parses as UNKNOWN
    assert bonus_2pc_inv_stat.value == 0.1

    # 2pc Invalid value type
    data_2pc_inv_val = {"stat": "HP", "value": "not a number"}
    bonus_2pc_inv_val = DriveDiscSetBonus.from_dict(2, data_2pc_inv_val)
    assert bonus_2pc_inv_val is not None # Returns default object on parse error
    assert bonus_2pc_inv_val.stat == Stat.UNKNOWN
    assert bonus_2pc_inv_val.value is None

    # --- Test 4-Piece ---
    # Valid 4pc
    data_4pc_valid = {
        "description": "Test desc {val1} and {val2}.",
        "values": {"val1": 10, "val2": "abc"}
    }
    bonus_4pc_valid = DriveDiscSetBonus.from_dict(4, data_4pc_valid)
    assert bonus_4pc_valid is not None
    assert bonus_4pc_valid.piece_count == 4
    assert bonus_4pc_valid.stat is None
    assert bonus_4pc_valid.value is None
    assert bonus_4pc_valid.description == "Test desc {val1} and {val2}."
    assert bonus_4pc_valid.values == {"val1": 10, "val2": "abc"}

    # 4pc Missing description
    data_4pc_no_desc = {"values": {"atk": 5}}
    bonus_4pc_no_desc = DriveDiscSetBonus.from_dict(4, data_4pc_no_desc)
    assert bonus_4pc_no_desc is not None
    assert bonus_4pc_no_desc.description is None
    assert bonus_4pc_no_desc.values == {"atk": 5}

    # 4pc Missing values
    data_4pc_no_vals = {"description": "No values here."}
    bonus_4pc_no_vals = DriveDiscSetBonus.from_dict(4, data_4pc_no_vals)
    assert bonus_4pc_no_vals is not None
    assert bonus_4pc_no_vals.description == "No values here."
    assert bonus_4pc_no_vals.values == {} # Defaults to empty dict

    # 4pc Invalid values type
    data_4pc_inv_vals = {"description": "Desc.", "values": "not a dict"}
    bonus_4pc_inv_vals = DriveDiscSetBonus.from_dict(4, data_4pc_inv_vals)
    assert bonus_4pc_inv_vals is not None
    assert bonus_4pc_inv_vals.description == "Desc."
    assert bonus_4pc_inv_vals.values == {} # Defaults to empty dict

    # --- Test General Edge Cases ---
    # None input
    assert DriveDiscSetBonus.from_dict(2, None) is None
    assert DriveDiscSetBonus.from_dict(4, None) is None
    # Invalid piece count
    assert DriveDiscSetBonus.from_dict(3, {"stat": "ATK"}) is None


def test_drivediscsetbonus_get_value_keys(woodpecker_4pc_bonus_obj, woodpecker_2pc_bonus_obj):
    """Test DriveDiscSetBonus.get_value_keys returns correct keys and handles 2pc/empty."""
    # Test with valid 4pc data
    assert woodpecker_4pc_bonus_obj is not None
    keys_4pc = woodpecker_4pc_bonus_obj.get_value_keys()
    assert isinstance(keys_4pc, list)
    assert set(keys_4pc) == {"atk", "duration"} # Use set for order-independent check

    # Test with 2pc bonus (should be empty)
    assert woodpecker_2pc_bonus_obj is not None
    keys_2pc = woodpecker_2pc_bonus_obj.get_value_keys()
    assert keys_2pc == []

    # Test with 4pc bonus having empty values dict
    bonus_empty_vals = DriveDiscSetBonus(piece_count=4, description="Desc", values={})
    keys_empty_vals = bonus_empty_vals.get_value_keys()
    assert keys_empty_vals == []


def test_drivediscsetbonus_get_formatted_description(woodpecker_4pc_bonus_obj, woodpecker_2pc_bonus_obj):
    """Test DriveDiscSetBonus.get_formatted_description for 4pc and edge cases."""
    # Test valid 4pc formatting
    assert woodpecker_4pc_bonus_obj is not None
    formatted = woodpecker_4pc_bonus_obj.get_formatted_description()
    assert isinstance(formatted, str)
    assert "ATK by 9%" in formatted
    assert "for 6s" in formatted

    # Test with 2pc bonus (should return original description, which is None)
    assert woodpecker_2pc_bonus_obj is not None
    assert woodpecker_2pc_bonus_obj.get_formatted_description() is None

    # Test 4pc with no description
    bonus_no_desc = DriveDiscSetBonus(piece_count=4, values={"val": 10})
    assert bonus_no_desc.get_formatted_description() is None

    # Test 4pc with no values (should return original description)
    original_desc = "Description with {placeholder}."
    bonus_no_vals = DriveDiscSetBonus(piece_count=4, description=original_desc, values={})
    assert bonus_no_vals.get_formatted_description() == original_desc

    # Test 4pc with missing key in values (placeholder remains)
    bonus_missing_key = DriveDiscSetBonus(
        piece_count=4,
        description="Value is {val1} and {val2}",
        values={"val1": 10} # Missing val2
    )
    formatted_missing = bonus_missing_key.get_formatted_description()
    assert formatted_missing == "Value is 10 and {val2}" # {val2} is not replaced


def test_drivediscsetdata_from_dict(woodpecker_dict):
    """Test DriveDiscSetData.from_dict parsing and defaults."""
    # --- Test Valid Full Data ---
    name = "Woodpecker Electro"
    obj_valid = DriveDiscSetData.from_dict(name, woodpecker_dict)
    assert obj_valid is not None
    assert isinstance(obj_valid, DriveDiscSetData)
    assert obj_valid.name == name
    # Check 2pc
    assert obj_valid.bonus_2pc is not None
    assert isinstance(obj_valid.bonus_2pc, DriveDiscSetBonus)
    assert obj_valid.bonus_2pc.piece_count == 2
    assert obj_valid.bonus_2pc.stat == Stat.CRIT_RATE
    assert obj_valid.bonus_2pc.value == 0.08
    # Check 4pc
    assert obj_valid.bonus_4pc is not None
    assert isinstance(obj_valid.bonus_4pc, DriveDiscSetBonus)
    assert obj_valid.bonus_4pc.piece_count == 4
    assert "Landing a critical hit" in obj_valid.bonus_4pc.description
    assert obj_valid.bonus_4pc.values == {"atk": 9, "duration": 6}

    # --- Test Missing 4-piece ---
    name_no_4pc = "Test Set No 4pc"
    data_no_4pc = {"2-piece": {"stat": "ATK", "value": 0.1}}
    obj_no_4pc = DriveDiscSetData.from_dict(name_no_4pc, data_no_4pc)
    assert obj_no_4pc is not None
    assert obj_no_4pc.name == name_no_4pc
    assert obj_no_4pc.bonus_2pc is not None
    assert obj_no_4pc.bonus_2pc.stat == Stat.ATK
    assert obj_no_4pc.bonus_4pc is None # Should be None

    # --- Test Missing 2-piece ---
    name_no_2pc = "Test Set No 2pc"
    data_no_2pc = {"4-piece": {"description": "Desc", "values": {}}}
    obj_no_2pc = DriveDiscSetData.from_dict(name_no_2pc, data_no_2pc)
    assert obj_no_2pc is not None
    assert obj_no_2pc.name == name_no_2pc
    assert obj_no_2pc.bonus_2pc is None # Should be None
    assert obj_no_2pc.bonus_4pc is not None
    assert obj_no_2pc.bonus_4pc.description == "Desc"

    # --- Test None Input ---
    assert DriveDiscSetData.from_dict("Some Name", None) is None

    # --- Test Empty Input ---
    # from_dict should return None if neither 2pc nor 4pc is parsed
    assert DriveDiscSetData.from_dict("Some Name", {}) is None