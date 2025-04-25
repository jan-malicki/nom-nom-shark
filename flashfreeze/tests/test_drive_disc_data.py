# tests/test_drive_disc_data.py

import pytest
import os
import sys
from unittest.mock import patch, MagicMock

from flashfreeze.core.drive_disc_data import EquippedDriveDisc, SubStatInstance
from flashfreeze.core.drive_disc_set_data import DriveDiscSetData # Needed for EquippedDriveDisc
from flashfreeze.core.common import Stat, Rarity


# --- Fixtures ---

@pytest.fixture
def mock_gdl():
    """ Mocks the game_data_loader module for isolated testing. """
    # Create a mock object that mimics the gdl module
    mock_gdl_obj = MagicMock()

    # --- Mock get_drive_substat_base_value ---
    # Define return values for specific inputs we'll use in tests
    substat_base_values = {
        (Rarity.S, Stat.ATK_PERCENT): 0.03,
        (Rarity.S, Stat.CRIT_RATE): 0.024,
        (Rarity.A, Stat.HP): 79.0,
        (Rarity.B, Stat.DEF): 5.0,
    }
    def mock_get_substat_base(rarity, stat_type):
        return substat_base_values.get((rarity, stat_type)) # Return None if not found
    mock_gdl_obj.get_drive_substat_base_value = MagicMock(side_effect=mock_get_substat_base)

    # --- Mock get_drive_main_stat_value ---
    main_stat_values = {
        # (Rarity, Stat, Level): Value
        (Rarity.S, Stat.ATK_PERCENT, 15): 0.30,
        (Rarity.S, Stat.ATK_PERCENT, 10): 0.20, # Example intermediate value
        (Rarity.S, Stat.ATK_PERCENT, 0): 0.05, # Example level 0 value
        (Rarity.A, Stat.HP, 12): 1468.0,
        (Rarity.B, Stat.DEF, 9): 60.0,
        # Add case for missing level 5, but existing level 15 (max for S)
        (Rarity.S, Stat.CRIT_RATE, 15): 0.24,
    }
    def mock_get_main_stat(rarity, stat_type, level):
        return main_stat_values.get((rarity, stat_type, level)) # Return None if not found
    mock_gdl_obj.get_drive_main_stat_value = MagicMock(side_effect=mock_get_main_stat)

    # Use patch to replace the actual gdl module within the test's scope
    # Adjust the target path ('flashfreeze.core.drive_disc_data.gdl') if your
    # import in drive_disc_data.py is different (e.g., 'zzzdata.game_data_loader')
    with patch('flashfreeze.core.drive_disc_data.gdl', mock_gdl_obj):
        yield mock_gdl_obj # Provide the mock to the test function if needed

@pytest.fixture
def dummy_set_data() -> DriveDiscSetData:
    """ Provides a basic DriveDiscSetData instance for tests. """
    # Parsing logic is tested elsewhere, just need a valid object structure
    return DriveDiscSetData(name="Test Set")


# --- Tests for SubStatInstance ---

@pytest.mark.usefixtures("mock_gdl") # Apply the mock for this test
@pytest.mark.parametrize("rarity, stat_type, rolls, expected_value", [
    (Rarity.S, Stat.ATK_PERCENT, 0, 0.03),    # Base value (0 rolls)
    (Rarity.S, Stat.ATK_PERCENT, 1, 0.06),    # 1 roll (base * 2)
    (Rarity.S, Stat.ATK_PERCENT, 5, 0.18),    # Max rolls (base * 6)
    (Rarity.S, Stat.CRIT_RATE, 3, 0.096),   # Intermediate rolls (base * 4)
    (Rarity.A, Stat.HP, 0, 79.0),
    (Rarity.B, Stat.DEF, 2, 15.0),      # base(5) * (2+1)
    # Test case where base value is not found in mock
    (Rarity.S, Stat.HP, 0, 0.0),           # Base value for HP S not mocked -> None -> 0.0
    # Test rolls exceeding max (should clamp to max)
    (Rarity.S, Stat.ATK_PERCENT, 6, 0.18),    # 6 rolls treated as 5 (base * 6)
])
def test_substatinstance_get_value(rarity, stat_type, rolls, expected_value):
    """Test SubStatInstance.get_value calculation using mocked base values."""
    substat = SubStatInstance(stat_type=stat_type, rolls=rolls)
    value = substat.get_value(rarity)
    assert value == pytest.approx(expected_value)

# --- Tests for EquippedDriveDisc ---

# Test __post_init__ Validations
def test_equipped_disc_post_init_valid(dummy_set_data):
    """Test successful creation with valid parameters."""
    try:
        EquippedDriveDisc(
            set_data=dummy_set_data, rarity=Rarity.S, level=15, slot=4,
            main_stat_type=Stat.ATK_PERCENT,
            sub_stats=[
                SubStatInstance(Stat.CRIT_RATE, 2),
                SubStatInstance(Stat.CRIT_DMG, 1),
                SubStatInstance(Stat.HP_PERCENT, 0),
                SubStatInstance(Stat.DEF, 2),
            ]
        )
    except (ValueError, TypeError) as e:
        pytest.fail(f"Valid EquippedDriveDisc raised an unexpected error: {e}")

@pytest.mark.parametrize("slot, main_stat, error_msg_part", [
    (0, Stat.HP, "Invalid slot number: 0"),                 # Invalid slot low
    (7, Stat.HP, "Invalid slot number: 7"),                 # Invalid slot high
    (1, Stat.ATK, "Invalid main stat 'ATK' for slot 1"),    # Wrong main stat for slot 1
    (4, Stat.HP, "Invalid main stat 'HP' for slot 4"),      # Wrong main stat for slot 4
    (5, Stat.CRIT_DMG, "Invalid main stat 'CRIT DMG' for slot 5"),      # Wrong main stat for slot 5
])
def test_equipped_disc_post_init_invalid_slot_main_stat(dummy_set_data, slot, main_stat, error_msg_part):
    """Test validation failures for slot and main stat combination."""
    with pytest.raises(ValueError) as excinfo:
        EquippedDriveDisc(
            set_data=dummy_set_data, rarity=Rarity.S, level=15, slot=slot,
            main_stat_type=main_stat, sub_stats=[]
        )
    assert error_msg_part in str(excinfo.value)

def test_equipped_disc_post_init_invalid_substat_count(dummy_set_data):
    """Test validation failure for too many substats."""
    with pytest.raises(ValueError) as excinfo:
        EquippedDriveDisc(
            set_data=dummy_set_data, rarity=Rarity.S, level=15, slot=4,
            main_stat_type=Stat.ATK_PERCENT,
            sub_stats=[ SubStatInstance(Stat.HP, 0) ] * 5 # 5 substats
        )
    assert "Cannot have more than 4 substats" in str(excinfo.value)

def test_equipped_disc_post_init_invalid_substat_type(dummy_set_data):
    """Test validation failure for invalid substat type."""
    with pytest.raises(ValueError) as excinfo:
        EquippedDriveDisc(
            set_data=dummy_set_data, rarity=Rarity.S, level=15, slot=4,
            main_stat_type=Stat.ATK_PERCENT,
            sub_stats=[ SubStatInstance(Stat.IMPACT, 0) ] # Impact not in POSSIBLE_SUBSTATS
        )
    assert "Invalid substat type: 'Impact'" in str(excinfo.value)

def test_equipped_disc_post_init_duplicate_substat(dummy_set_data):
    """Test validation failure for duplicate substat types."""
    with pytest.raises(ValueError) as excinfo:
        EquippedDriveDisc(
            set_data=dummy_set_data, rarity=Rarity.S, level=15, slot=4,
            main_stat_type=Stat.ATK_PERCENT,
            sub_stats=[ SubStatInstance(Stat.HP, 0), SubStatInstance(Stat.HP, 1) ] # Duplicate HP
        )
    assert "Duplicate substat type found: 'HP'" in str(excinfo.value)

def test_equipped_disc_post_init_substat_equals_mainstat(dummy_set_data):
    """Test validation failure when a substat matches the main stat."""
    with pytest.raises(ValueError) as excinfo:
        EquippedDriveDisc(
            set_data=dummy_set_data, rarity=Rarity.S, level=15, slot=4,
            main_stat_type=Stat.ATK_PERCENT,
            sub_stats=[ SubStatInstance(Stat.ATK_PERCENT, 0) ] # Substat matches main
        )
    assert "cannot be the same as main stat" in str(excinfo.value)

def test_equipped_disc_post_init_invalid_substat_rolls(dummy_set_data):
    """Test validation failure for invalid number of substat rolls."""
    with pytest.raises(ValueError) as excinfo:
        EquippedDriveDisc(
            set_data=dummy_set_data, rarity=Rarity.S, level=15, slot=4,
            main_stat_type=Stat.ATK_PERCENT,
            sub_stats=[ SubStatInstance(Stat.HP, 6) ] # 6 rolls is invalid (max 5)
        )
    assert "Invalid number of rolls (6)" in str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        EquippedDriveDisc(
            set_data=dummy_set_data, rarity=Rarity.S, level=15, slot=4,
            main_stat_type=Stat.ATK_PERCENT,
            sub_stats=[ SubStatInstance(Stat.HP, -1) ] # Negative rolls invalid
        )
    assert "Invalid number of rolls (-1)" in str(excinfo.value)

def test_equipped_disc_post_init_invalid_substat_rolls(dummy_set_data):
    """Test validation failure for invalid number of substat rolls."""
    with pytest.raises(ValueError) as excinfo:
        EquippedDriveDisc(
            set_data=dummy_set_data, rarity=Rarity.S, level=15, slot=4,
            main_stat_type=Stat.ATK_PERCENT,
            sub_stats=[ SubStatInstance(Stat.HP, 3), SubStatInstance(Stat.ATK, 3) ] # Negative rolls invalid
        )
    assert "Total substat rolls (6) exceed maximum allowed (5)" in str(excinfo.value)

def test_equipped_disc_post_init_level_clamping(dummy_set_data):
    """Test that level is clamped based on rarity during init."""
    # S rank, level 20 -> clamped to 15
    disc_s = EquippedDriveDisc(dummy_set_data, Rarity.S, 20, 1, Stat.HP, [])
    assert disc_s.level == 15
    # A rank, level 15 -> clamped to 12
    disc_a = EquippedDriveDisc(dummy_set_data, Rarity.A, 15, 1, Stat.HP, [])
    assert disc_a.level == 12
    # B rank, level 10 -> clamped to 9
    disc_b = EquippedDriveDisc(dummy_set_data, Rarity.B, 10, 1, Stat.HP, [])
    assert disc_b.level == 9
    # Negative level -> clamped to 0
    disc_neg = EquippedDriveDisc(dummy_set_data, Rarity.S, -5, 1, Stat.HP, [])
    assert disc_neg.level == 0


# Test EquippedDriveDisc Methods
@pytest.mark.usefixtures("mock_gdl") # Apply the mock for these tests
def test_equipped_disc_get_main_stat_value(dummy_set_data):
    """Test get_main_stat_value using mocked gdl function."""
    # Test existing value
    disc1 = EquippedDriveDisc(dummy_set_data, Rarity.S, 15, 4, Stat.ATK_PERCENT, [])
    assert disc1.get_main_stat_value() == pytest.approx(0.30)
    disc2 = EquippedDriveDisc(dummy_set_data, Rarity.S, 10, 4, Stat.ATK_PERCENT, [])
    assert disc2.get_main_stat_value() == pytest.approx(0.20)

    # Test missing level - fallback to max level
    # Mock setup: get(S, CRIT_RATE, 5) returns None, get(S, CRIT_RATE, 15) returns 0.24
    disc3 = EquippedDriveDisc(dummy_set_data, Rarity.S, 5, 4, Stat.CRIT_RATE, [])
    assert disc3.get_main_stat_value() == pytest.approx(0.24) # Falls back to level 15 value


@pytest.mark.usefixtures("mock_gdl") # Apply the mock for this test
def test_equipped_disc_get_all_substat_values(dummy_set_data):
    """Test get_all_substat_values aggregates correctly using mocked base values."""
    disc = EquippedDriveDisc(
        set_data=dummy_set_data, rarity=Rarity.S, level=15, slot=4,
        main_stat_type=Stat.CRIT_DMG,
        sub_stats=[
            SubStatInstance(Stat.CRIT_RATE, 3), # Base 0.024 -> 0.024 * 4 = 0.096
            SubStatInstance(Stat.ATK_PERCENT, 1), # Base 0.03 -> 0.03 * 2 = 0.06
            SubStatInstance(Stat.HP, 0), # Base for HP S not mocked -> 0.0
        ]
    )
    expected_values = {
        Stat.CRIT_RATE: 0.096,
        Stat.ATK_PERCENT: 0.06,
        Stat.HP: 0.0,
    }
    actual_values = disc.get_all_substat_values()
    assert actual_values.keys() == expected_values.keys()
    for stat, expected in expected_values.items():
        assert actual_values[stat] == pytest.approx(expected)

    # Test with no substats
    disc_no_subs = EquippedDriveDisc(dummy_set_data, Rarity.S, 15, 1, Stat.HP, [])
    assert disc_no_subs.get_all_substat_values() == {}

