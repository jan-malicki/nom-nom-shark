# tests/test_game_data_loader.py

import pytest
import os
import sys
import json
from decimal import Decimal, InvalidOperation # Use Decimal for precision

from flashfreeze.core.agent_data import AgentData
from flashfreeze.core.common import Attribute, Rarity, Faction, Stat, SkillType
from flashfreeze.core.skill_data import AgentSkillData
from flashfreeze import game_data_loader as gdl

# --- Pytest Fixtures ---

@pytest.fixture(scope="module") # Load skills data once per test module
def all_skills_data() -> AgentSkillData:
    """Fixture to load skills data from JSON."""
    data = gdl.get_agent_skill_data(gdl.ELLEN_SKILLS_FILE)
    if not data:
        pytest.fail(f"Failed to load required test data from {gdl.ELLEN_SKILLS_FILE}")
    return data

# --- Test Functions ---

def test_load_known_w_engine():
    """Test loading data for a W-Engine expected to be in the JSON."""
    # --- ARRANGE ---
    known_engine_name = "Steel Cushion"

    # --- ACT ---
    engine_data = gdl.get_w_engine_data(known_engine_name)

    # --- ASSERT ---
    assert engine_data is not None, f"Data for known W-Engine '{known_engine_name}' should be loaded."
    assert isinstance(engine_data, dict), f"Data for '{known_engine_name}' should be a dictionary."
    # Add more specific checks if needed, e.g.:
    # assert "rarity" in engine_data
    # assert engine_data.get("type") == "Strike"

def test_load_unknown_w_engine():
    """Test loading data for a W-Engine name not expected in the JSON."""
    # --- ARRANGE ---
    unknown_engine_name = "Definitely Not A Real Engine"

    # --- ACT ---
    engine_data = gdl.get_w_engine_data(unknown_engine_name)

    # --- ASSERT ---
    assert engine_data is None, f"Data for unknown W-Engine '{unknown_engine_name}' should be None."

def test_load_known_agent():
    """Test retrieving the list of all agent IDs."""
    # --- ARRANGE ---
    # Assumes agents.json exists and is not empty

    # --- ACT ---
    agent_names = gdl.get_all_agent_names()

    # --- ASSERT ---
    assert isinstance(agent_names, list), "Should return a list of agent IDs."
    assert len(agent_names) > 0, "Agent ID list should not be empty (assuming data exists)."
    assert "Ellen" in agent_names, "A known agent ID should be in the list."

def test_load_agent_skill_data():
    """Test loading data for a known agent's skills."""
    # --- ARRANGE ---
    agent_filename = gdl.ELLEN_SKILLS_FILE

    # --- ACT ---
    skill_data = gdl.get_agent_skill_data(agent_filename)

    # --- ASSERT ---
    assert skill_data is not None, f"Skill data for known agent '{agent_filename}' should be loaded."
    assert isinstance(skill_data, AgentSkillData), f"Data for '{agent_filename}' should be an AgentSkillData object."

def test_load_agent_data():
    """Test retrieving data for a known agent returns an AgentData object."""
    # --- ARRANGE ---
    agent_name = "Ellen"

    # --- ACT ---
    # Assumes get_agent_data is corrected to return Optional[AgentData]
    agent_obj = gdl.get_agent_data(agent_name)

    # --- ASSERT ---
    assert agent_obj is not None, f"Agent '{agent_name}' should be found."
    assert isinstance(agent_obj, AgentData), "Result should be an AgentData instance."
    assert agent_obj.name == agent_name
    assert agent_obj.attribute == Attribute.ICE # Check a specific parsed field
    assert agent_obj.rarity == Rarity.S
    assert agent_obj.base_stats.atk == 938 # Check a nested base stat
    assert agent_obj.core_stat.stat == Stat.CRIT_RATE # Check core stat enum
    assert agent_obj.core_stat.value == 0.144 # Check core stat value
    assert agent_obj.info.full_name == "Ellen Joe" # Check info block

@pytest.mark.parametrize("rarity, stat_type, expected_value", [
    # S Rank
    (Rarity.S, Stat.HP, 112.0),
    (Rarity.S, Stat.ATK_PERCENT, 0.03), # 3 / 100
    (Rarity.S, Stat.CRIT_RATE, 0.024), # 2.4 / 100
    (Rarity.S, Stat.CRIT_DMG, 0.048), # 4.8 / 100
    (Rarity.S, Stat.PEN, 9.0),
    # A Rank
    (Rarity.A, Stat.DEF, 10.0),
    (Rarity.A, Stat.DEF_PERCENT, 0.032), # 3.2 / 100
    (Rarity.A, Stat.ANOMALY_PROFICIENCY, 6.0),
    # B Rank
    (Rarity.B, Stat.HP_PERCENT, 0.01), # 1 / 100
    (Rarity.B, Stat.PEN, 3.0),
    # Edge cases
    (Rarity.S, Stat.IMPACT, None), # Impact is not a substat in the provided JSON
    (Rarity.C, Stat.ATK, None), # Rarity C not in substat JSON
])
def test_get_drive_substat_base_value(rarity, stat_type, expected_value):
    """Test fetching drive disc substat base values."""
    value = gdl.get_drive_substat_base_value(rarity, stat_type)
    if expected_value is None:
        assert value is None
    else:
        assert value == pytest.approx(expected_value)

@pytest.mark.parametrize("rarity, stat_type, level, expected_value", [
    # S Rank Main Stats
    (Rarity.S, Stat.HP, 15, 2200.0),
    (Rarity.S, Stat.HP, 0, 550.0),
    (Rarity.S, Stat.ATK, 15, 316.0),
    (Rarity.S, Stat.DEF, 15, 184.0),
    (Rarity.S, Stat.HP_PERCENT, 15, 0.30), # 30 / 100
    (Rarity.S, Stat.ATK_PERCENT, 15, 0.30), # 30 / 100
    (Rarity.S, Stat.FIRE_DMG, 15, 0.30), # 30 / 100
    (Rarity.S, Stat.DEF_PERCENT, 15, 0.48), # 48 / 100
    (Rarity.S, Stat.PEN_RATIO, 15, 0.24), # 24 / 100
    (Rarity.S, Stat.CRIT_RATE, 15, 0.24), # 24 / 100
    (Rarity.S, Stat.CRIT_DMG, 15, 0.48), # 48 / 100
    (Rarity.S, Stat.ANOMALY_PROFICIENCY, 15, 92.0),
    (Rarity.S, Stat.ENERGY_REGEN, 15, 0.60), # 60 / 100
    (Rarity.S, Stat.IMPACT, 15, 18.0),
    # A Rank Main Stats (Max Level 12)
    (Rarity.A, Stat.HP, 12, 1468.0),
    (Rarity.A, Stat.ATK, 12, 212.0),
    (Rarity.A, Stat.CRIT_DMG, 12, 0.32), # 32 / 100
    # B Rank Main Stats (Max Level 9)
    (Rarity.B, Stat.DEF, 9, 60.0),
    (Rarity.B, Stat.HP_PERCENT, 9, 0.10), # 10 / 100
    # Missing Level (Expect None from loader)
    (Rarity.S, Stat.HP_PERCENT, 1, None), # Level 1 not defined for HP% S rank
    (Rarity.A, Stat.ATK, 0, None), # Level 0 not defined for ATK A rank
    # Non-existent stat/rarity combo
    (Rarity.S, Stat.PEN, 15, None), # PEN is not a main stat
    (Rarity.C, Stat.HP, 9, None), # Rarity C not defined
])
def test_get_drive_main_stat_value(rarity, stat_type, level, expected_value):
    """Test fetching drive disc main stat values for various levels/rarities."""
    value = gdl.get_drive_main_stat_value(rarity, stat_type, level)
    if expected_value is None:
        assert value is None
    else:
        # Use approx for float comparisons
        assert value == pytest.approx(expected_value)

def test_skill_scaling_integrity(all_skills_data: AgentSkillData): # Fixture is injected here
    """
    Verify that Level 1 Value + (Step Value * 15) == Level 16 Value
    for dmg_scaling and daze_scaling entries using AgentSkillData object.
    """
    # --- ARRANGE ---
    # Data object is provided by the 'all_skills_data' fixture
    mismatches = [] # Store details of skills that fail the check

    # --- ACT ---
    # Outer loop: Iterate through AbilityData objects in all_skills_data.skills
    for skill_name, skill_obj in all_skills_data.skills.items():
        # Inner loop: Iterate through MultiplierData objects in skill_obj.multipliers
        for multiplier_name, multiplier_obj in skill_obj.multipliers.items():

            # --- Check scaling ---
            scaling_checks = []
            if multiplier_obj.dmg_scaling:
                scaling_checks.append(("DMG", multiplier_obj.dmg_scaling))
            if multiplier_obj.daze_scaling:
                scaling_checks.append(("Daze", multiplier_obj.daze_scaling))

            for scaling_label, scaling_data in scaling_checks:
                # Check required attributes exist (dataclass ensures they do, but check values)
                try:
                    # Access attributes directly
                    val_l1 = Decimal(str(scaling_data.level_1))
                    val_step = Decimal(str(scaling_data.step))
                    val_l16_expected = Decimal(str(scaling_data.level_16))

                    calculated_l16 = val_l1 + (val_step * Decimal(15))

                    if not abs(calculated_l16 - val_l16_expected) < Decimal('0.0001'):
                        mismatches.append(
                            f"Mismatch in '{skill_name}' -> '{multiplier_name}' ({scaling_label}): "
                            f"Expected level 16 value {val_l16_expected}, but calculated {calculated_l16} "
                            f"(Level 1: {val_l1}, step: {val_step})"
                        )
                except (InvalidOperation, ValueError, TypeError) as e:
                    mismatches.append(
                        f"Error in '{skill_name}' -> '{multiplier_name}' ({scaling_label}): Processing values - {e}. "
                        f"L1='{getattr(scaling_data, 'level_1', 'N/A')}', "
                        f"Step='{getattr(scaling_data, 'step', 'N/A')}', "
                        f"L16='{getattr(scaling_data, 'level_16', 'N/A')}'"
                    )

            # --- Check hit count and damage spread ---
            # Access attributes directly from multiplier_obj
            hit_count = multiplier_obj.hit_count
            damage_spread = multiplier_obj.damage_spread

            if not isinstance(hit_count, int) or hit_count <= 0:
                 mismatches.append(
                     f"Skill '{skill_name}' -> '{multiplier_name}': Invalid hit count '{hit_count}'. Must be a positive integer."
                 )
            # Only check spread if hit_count is valid and spread exists
            elif damage_spread: # Check if list is not empty/None
                if not isinstance(damage_spread, list):
                     mismatches.append(
                         f"Skill '{skill_name}' -> '{multiplier_name}': 'damage_spread' is not a list."
                     )
                elif len(damage_spread) != hit_count:
                     mismatches.append(
                         f"Skill '{skill_name}' -> '{multiplier_name}': 'damage_spread' length ({len(damage_spread)}) does not match hit count ({hit_count})."
                     )
                else:
                    try:
                        # Ensure all values in spread are convertible to Decimal
                        spread_sum = sum(Decimal(str(value)) for value in damage_spread)
                        # Use a slightly larger tolerance for sums
                        if not abs(spread_sum - Decimal('1.0')) <= Decimal('0.0001'):
                             mismatches.append(
                                 f"Skill '{skill_name}' -> '{multiplier_name}': 'damage_spread' values sum to {spread_sum}, "
                                 f"which is not approximately 1.0 (error tolerance: 0.0001)."
                             )
                    except (InvalidOperation, ValueError, TypeError) as e:
                         mismatches.append(
                             f"Skill '{skill_name}' -> '{multiplier_name}': Error processing 'damage_spread' values - {e}."
                         )

    # --- ASSERT ---
    # Final assertion after checking all skills and multipliers
    assert not mismatches, "Found skill data integrity issues:\n" + "\n".join(mismatches)