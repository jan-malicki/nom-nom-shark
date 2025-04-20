import pytest
import os
import sys
import json
from decimal import Decimal, InvalidOperation # Use Decimal for precision

try:
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nom_nom_shark.settings') # Adjust project name
    # django.setup() # pytest-django handles this; avoid calling directly in test files
except ImportError:
    print("Warning: Django not found or DJANGO_SETTINGS_MODULE not set.")
    print("Data loader might fail if it depends on Django settings.")

# Attempt to import the game data loader module
try:
    from flashfreeze import game_data_loader as gdl
except ImportError:
    print("Error: Could not import 'flashfreeze.game_data_loader'.")
    print("Ensure this test script is runnable from your project structure,")
    print("and the project root is correctly added to sys.path.")
    sys.exit(1) # Exit if loader can't be imported
except Exception as e:
    print(f"An unexpected error occurred during import: {e}")
    sys.exit(1)

# --- Pytest Fixtures ---

@pytest.fixture(scope="module") # Load skills data once per test module
def all_skills_data():
    """Fixture to load skills data from JSON."""
    data = gdl._load_json_data(gdl.ELLEN_SKILLS_FILE)
    if not data:
        pytest.fail(f"Failed to load required test data from {gdl.ELLEN_SKILLS_FILE}")
    return data.get("Skills", {}) # Return the 'skills' part of the data

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

def test_load_skill_data():
    """Test loading data for a known skill."""
    # --- ARRANGE ---
    agent_filename = gdl.ELLEN_SKILLS_FILE
    skill_name = "Basic Attack: Saw Teeth Trimming"

    # --- ACT ---
    skill_data = gdl.get_skill_data(agent_filename, skill_name)

    # --- ASSERT ---
    assert skill_data is not None, f"Data for known skill '{skill_name}' should be loaded."
    assert isinstance(skill_data, dict), f"Data for '{skill_name}' should be a dictionary."

def test_skill_scaling_integrity(all_skills_data): # Fixture is injected here
    """
    Verify that Level 1 Value + (Step Value * 15) == Level 16 Value
    for dmg_scaling and daze_scaling entries in skills.json.
    Handles structure: Skill -> Multiplier -> [dmg_scaling | daze_scaling].
    """
    # --- ARRANGE ---
    # Data is loaded by the 'all_skills_data' fixture

    # Define the keys expected within the 'dmg_scaling' or 'daze_scaling' dictionary
    level_1_key = "1"
    step_key = "step"
    level_16_key = "16"
    required_keys = {level_1_key, step_key, level_16_key}

    mismatches = [] # Store details of skills that fail the check

    # --- ACT ---
    # Outer loop: Iterate through main skill names (e.g., "Basic Attack: Saw Teeth Trimming")
    for skill_name, skill_data in all_skills_data.items():
        if not isinstance(skill_data, dict):
            continue

        # Inner loop: Iterate through multipliers (e.g., "1st-Hit Multiplier")
        for multiplier_name, multiplier_data in skill_data.items():
            if not isinstance(multiplier_data, dict):
                # Skip entries that aren't dictionaries (like "Flash Freeze Charge Obtained")
                print(f"Info: Skipping multiplier '{multiplier_name}', data is not a dictionary.")
                continue

            # --- Check scaling ---
            for scaling in ["dmg_scaling", "daze_scaling"]:
                if scaling in multiplier_data:
                    current_level_data = multiplier_data[scaling]

                    if not isinstance(current_level_data, dict):
                        mismatches.append(
                            f"Skill '{skill_name}' -> '{multiplier_name}' ({scaling}): Scaling data is not a dictionary."
                        )
                    elif not required_keys.issubset(current_level_data.keys()):
                        missing = required_keys - set(current_level_data.keys())
                        mismatches.append(
                            f"Skill '{skill_name}' -> '{multiplier_name}' ({scaling}): Missing scaling keys: {missing}"
                        )
                    else:
                        try:
                            val_l1 = Decimal(str(current_level_data[level_1_key]))
                            val_step = Decimal(str(current_level_data[step_key]))
                            val_l16_expected = Decimal(str(current_level_data[level_16_key]))
                            calculated_l16 = val_l1 + (val_step * Decimal(15))

                            if not abs(calculated_l16 - val_l16_expected) < Decimal('0.0001'):
                                mismatches.append(
                                    f"Mismatch in '{skill_name}' -> '{multiplier_name}' ({scaling}): "
                                    f"Expected level 16 value {val_l16_expected}, but calculated {calculated_l16} "
                                    f"(Level 1: {val_l1}, step: {val_step})"
                                )
                        except (InvalidOperation, ValueError, TypeError) as e:
                            mismatches.append(
                                f"Error in '{skill_name}' -> '{multiplier_name}' ({scaling}): Processing values - {e}. "
                                f"Level 1='{current_level_data.get(level_1_key)}', step='{current_level_data.get(step_key)}', level 16='{current_level_data.get(level_16_key)}'"
                            )
                        except KeyError as e:
                            mismatches.append(f"Error in '{skill_name}' -> '{multiplier_name}' ({scaling}): Missing key {e} during calculation.")

            # --- Check hit count and damage spread ---
            if "hit_count" in multiplier_data:
                hit_count = multiplier_data["hit_count"]
                if not isinstance(hit_count, int) or hit_count <= 0:
                    mismatches.append(
                        f"Skill '{skill_name}' -> '{multiplier_name}': Invalid hit count '{hit_count}'. Must be a positive integer."
                    )
                elif "damage_spread" in multiplier_data:
                    damage_spread = multiplier_data["damage_spread"]
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
                            spread_sum = sum(Decimal(str(value)) for value in damage_spread)
                            if not abs(spread_sum - Decimal('1.0')) <= Decimal('0.01'):
                                mismatches.append(
                                    f"Skill '{skill_name}' -> '{multiplier_name}': 'damage_spread' values sum to {spread_sum}, "
                                    f"which is not approximately 1.0 (error tolerance: 0.01)."
                                )
                        except (InvalidOperation, ValueError, TypeError) as e:
                            mismatches.append(
                                f"Skill '{skill_name}' -> '{multiplier_name}': Error processing 'damage_spread' values - {e}."
                            )


    # --- ASSERT ---
    # Final assertion after checking all skills and multipliers
    assert not mismatches, "Found skill scaling mismatches:\n" + "\n".join(mismatches)
