import json
import os
from functools import lru_cache
from typing import Dict, Any, Optional, List, Set

from flashfreeze.core.common import Stat, Rarity

# Define the directory where your static JSON data is stored
LOADER_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DATA_DIR = os.path.join(LOADER_DIR, 'resources', 'game_data')

# Define filenames for clarity
AGENTS_FILE = 'agents.json'
W_ENGINES_FILE = 'w-engines.json'
DRIVE_DISCS_SETS_FILE = 'drive_discs.json'
DRIVE_DISCS_MAIN_STATS_FILE = 'drive_discs_mainstat_values.json'
DRIVE_DISCS_SUB_STATS_FILE = 'drive_discs_substat_values.json'
ENEMIES_FILE = 'enemies.json'

SKILLS_DIR = 'skills'
ELLEN_SKILLS_FILE = os.path.join(SKILLS_DIR, 'ellen.json')

# --- Private Helper Function with Caching ---

@lru_cache(maxsize=None) # Cache results indefinitely
def _load_json_data(filename: str) -> Dict[str, Any]:
    """
    Loads and parses a JSON file from the STATIC_DATA_DIR.
    Handles file not found and JSON decoding errors.
    Results are cached using lru_cache.

    Args:
        filename: The name of the JSON file to load (e.g., 'w_engines.json').

    Returns:
        A dictionary containing the parsed JSON data.
        Returns an empty dictionary if the file is not found or invalid.
    """
    filepath = os.path.join(STATIC_DATA_DIR, filename)
    try:
        # Ensure UTF-8 encoding is used for broader compatibility
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, dict):
                print(f"Warning: Root element in {filename} is not a dictionary.")
                return {}
            return data
    except FileNotFoundError:
        print(f"Error: Static data file not found at {filepath}")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {filepath}")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred loading {filepath}: {e}")
        return {}

# --- Public Data Access Functions ---

def get_w_engine_data(engine_name: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves data for a specific W-Engine by its name.

    Args:
        engine_name: The name (key) of the W-Engine.

    Returns:
        A dictionary containing the W-Engine's data, or None if not found.
    """
    all_engines = _load_json_data(W_ENGINES_FILE)
    return all_engines.get(engine_name)

def get_all_w_engine_names() -> List[str]:
    """Returns a list of all W-Engine names."""
    all_engines = _load_json_data(W_ENGINES_FILE)
    return list(all_engines.keys())

def get_all_agent_names() -> List[str]:
    """Returns a list of all Agent names."""
    all_agents = _load_json_data(AGENTS_FILE)
    return list(all_agents.keys())

def get_agent_data(agent_name: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves Agent's data by its name.

    Args:
        agent_name: The desired Agent's name.

    Returns:
        An AgentData object containing the Agent's data, or empty if not found.
    """
    agent_dict = _load_json_data(AGENTS_FILE)
    return agent_dict.get(agent_name)

def get_agent_skill_data(agent_filename: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves data for an Agent's skillset by its name.

    Args:
        agent_filename: The filename of the Agent's skillset file.

    Returns:
        An AgentSkillData object containing the Agent's skill data, or empty if not found.
    """
    skills_dict = _load_json_data(agent_filename)
    return skills_dict

def get_drive_disc_set_data(set_name: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves data for a specific Drive Disc set by its name.

    Args:
        set_name: The name (key) of the Drive Disc set.

    Returns:
        A dictionary containing the set's data (e.g., 2pc/4pc bonuses),
        or None if not found.
    """
    all_sets = _load_json_data(DRIVE_DISCS_SETS_FILE)
    return all_sets.get(set_name)

def get_drive_main_stat_value(rarity: Rarity, stat_type: Stat, level: int) -> Optional[float]:
    """
    Retrieves the main stat value for a Drive Disc.

    Args:
        rarity: The Rarity enum member (e.g., Rarity.S).
        stat_type: The Stat enum member (e.g., Stat.ATK_PERCENT).
        level: The integer level of the disc (0-15).

    Returns:
        The calculated stat value as a float (percentage stats divided by 100),
        or None if the value for the specific stat/rarity/level combination
        is not found in the JSON.
    """
    all_main_stats = _load_json_data(DRIVE_DISCS_MAIN_STATS_FILE)

    # Use Enum values for keys (e.g., "HP%", "S")
    if stat_type in Stat.get_damage_bonus_stats():
        stat_key = "DMG"
    else:
        stat_key = stat_type.value
    rarity_key = rarity.value # Assumes Rarity enum values are "S", "A", "B"
    level_key = str(level)

    # Navigate the dictionary safely using .get()
    stat_data = all_main_stats.get(stat_key, {})
    rarity_data = stat_data.get(rarity_key, {})
    raw_value = rarity_data.get(level_key)

    if raw_value is None:
        # Value for this specific level not found
        # Could add interpolation later if needed
        return None

    try:
        return float(raw_value)
    except (ValueError, TypeError):
        print(f"Warning: Could not convert main stat value '{raw_value}' to float for {stat_key}/{rarity_key}/{level_key}")
        return None

def get_drive_substat_base_value(rarity: Rarity, stat_type: Stat) -> Optional[float]:
    """
    Retrieves the base value (value per roll/initial value) for a Drive Disc substat.

    Args:
        rarity: The Rarity enum member (e.g., Rarity.S).
        stat_type: The Stat enum member (e.g., Stat.CRIT_RATE).

    Returns:
        The base stat value as a float (percentage stats divided by 100),
        or None if the value for the specific stat/rarity combination
        is not found in the JSON.
    """
    all_sub_stats = _load_json_data(DRIVE_DISCS_SUB_STATS_FILE)

    # Use Enum values for keys (e.g., "HP%", "S")
    stat_key = stat_type.value
    rarity_key = rarity.value # Assumes Rarity enum values are "S", "A", "B"

    # Navigate safely
    stat_data = all_sub_stats.get(stat_key, {})
    raw_value = stat_data.get(rarity_key)

    if raw_value is None:
        return None

    try:
        return float(raw_value)
    except (ValueError, TypeError):
        print(f"Warning: Could not convert substat value '{raw_value}' to float for {stat_key}/{rarity_key}")
        return None

def get_enemy_data(enemy_name: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves data for a specific Enemy by its name.

    Args:
        enemy_name: The name (key) of the Enemy.

    Returns:
        A dictionary containing the Enemy's data, or None if not found.
    """
    all_enemies = _load_json_data(ENEMIES_FILE)
    return all_enemies.get(enemy_name)

# --- Potentially More Complex Access Logic ---
# Example: Getting a W-Engine's base ATK at a specific level

def get_w_engine_stats(engine_name: str, level: int) -> Optional[float]:
    """
    Gets the base ATK for a W-Engine at a specific level.
    Assumes the engine data contains a 'base_atk_scaling' dictionary
    with levels as string keys.

    Args:
        engine_name: The name of the W-Engine.
        level: The target level (integer).

    Returns:
        The base ATK as a float, or None if data is missing/invalid.
    """
    engine_data = get_w_engine_data(engine_name)
    if not engine_data:
        return None

    scaling_data = engine_data.get('base_atk_scaling')
    if not isinstance(scaling_data, dict):
        print(f"Warning: Missing or invalid 'base_atk_scaling' for {engine_name}")
        return None

    # Levels in JSON might be strings, convert level to string for lookup
    level_str = str(level)
    base_atk = scaling_data.get(level_str)

    if base_atk is None:
        # Optional: Add interpolation logic here if needed for levels
        # not explicitly listed in the JSON. For now, return None.
        print(f"Warning: Level {level} not found in 'base_atk_scaling' for {engine_name}")
        return None

    try:
        return float(base_atk)
    except (ValueError, TypeError):
        print(f"Warning: Invalid base ATK value '{base_atk}' for {engine_name} at level {level}")
        return None

# Add similar specific accessor functions as needed for other data types
# (e.g., getting skill multipliers, passive effects based on refinement, etc.)

