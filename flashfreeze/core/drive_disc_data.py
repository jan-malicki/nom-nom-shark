# core/drive_disc_data.py

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set

from .common import Stat, Rarity
from .drive_disc_set_data import DriveDiscSetData # To link equipped disc to its set bonus info
# Import game_data_loader to fetch main/sub stat values from JSON
from .. import game_data_loader as gdl

# --- Constants Defining Drive Disc Rules ---

# Using Stat Enum members directly
# Make sure Stat enum includes HP_PERCENT, ATK_PERCENT, DEF_PERCENT etc.
POSSIBLE_MAIN_STATS_PER_SLOT: Dict[int, List[Stat]] = {
    1: [Stat.HP],
    2: [Stat.ATK],
    3: [Stat.DEF],
    4: [Stat.HP_PERCENT, Stat.ATK_PERCENT, Stat.DEF_PERCENT, Stat.CRIT_RATE, Stat.CRIT_DMG, Stat.ANOMALY_PROFICIENCY],
    5: [Stat.HP_PERCENT, Stat.ATK_PERCENT, Stat.DEF_PERCENT, Stat.PEN_RATIO, Stat.PHYSICAL_DMG, Stat.FIRE_DMG, Stat.ICE_DMG, Stat.ELECTRIC_DMG, Stat.ETHER_DMG],
    6: [Stat.HP_PERCENT, Stat.ATK_PERCENT, Stat.DEF_PERCENT, Stat.ANOMALY_MASTERY, Stat.IMPACT, Stat.ENERGY_REGEN]
}

POSSIBLE_SUBSTATS: Set[Stat] = { # Use a set for faster lookups
    Stat.HP, Stat.ATK, Stat.DEF, Stat.HP_PERCENT, Stat.ATK_PERCENT, Stat.DEF_PERCENT,
    Stat.PEN, Stat.CRIT_RATE, Stat.CRIT_DMG, Stat.ANOMALY_PROFICIENCY
}

MAX_LEVEL_PER_RARITY: Dict[Rarity, int] = {
    Rarity.B: 9,
    Rarity.A: 12,
    Rarity.S: 15
}

# Min/Max starting substats
STARTING_SUBSTATS_PER_RARITY: Dict[Rarity, Tuple[int, int]] = {
    Rarity.B: (1, 2),
    Rarity.A: (2, 3),
    Rarity.S: (3, 4)
}

# Levels at which substat upgrades/additions occur
SUBSTAT_UPGRADE_LEVELS: List[int] = [3, 6, 9, 12, 15]

MAX_SUBSTATS_COUNT: int = 4
MAX_SUBSTAT_ROLLS: int = 5 # Max number of *upgrades* (total value multiplier is rolls+1)

# --- Core Logic Classes ---

@dataclass
class SubStatInstance:
    """Represents a specific substat on an equipped Drive Disc."""
    stat_type: Stat
    # Number of times this substat has been rolled/upgraded (starts at 0 for initial value)
    rolls: int = 0 # 0 means base value, 1 means base + 1 upgrade, etc.

    def get_value(self, rarity: Rarity) -> float:
        """
        Calculates the value of this substat based on its type, rarity, and rolls.
        Uses gdl to fetch base values.
        """
        # 1. Get base value from game_data_loader
        base_value = gdl.get_drive_substat_base_value(rarity, self.stat_type)
        if base_value is None:
            print(f"Warning: Base value not found for substat {self.stat_type.name} (Rarity: {rarity.name}). Returning 0.")
            return 0.0

        # 2. Calculate final value: base * (rolls + 1)
        # Clamp rolls just in case (shouldn't exceed MAX_SUBSTAT_ROLLS)
        actual_rolls = min(self.rolls, MAX_SUBSTAT_ROLLS)
        final_value = base_value * (actual_rolls + 1)

        return final_value


@dataclass
class DriveDisc:
    """Represents a specific Drive Disc instance to be equipped by an agent."""
    # Reference to the static set data (loaded elsewhere)
    set_data: DriveDiscSetData
    rarity: Rarity
    level: int # Current level (0-15)
    slot: int  # Slot number (1-6)
    main_stat_type: Stat
    sub_stats: List[SubStatInstance] = field(default_factory=list)

    def __post_init__(self):
        """Validate data after initialization."""
        # Clamp level based on rarity
        max_level = MAX_LEVEL_PER_RARITY.get(self.rarity, 0)
        self.level = max(0, min(self.level, max_level))

        # Validate slot
        if not 1 <= self.slot <= 6:
            raise ValueError(f"Invalid slot number: {self.slot}. Must be 1-6.")

        # Validate main stat for slot
        if self.main_stat_type not in POSSIBLE_MAIN_STATS_PER_SLOT.get(self.slot, []):
             raise ValueError(f"Invalid main stat '{self.main_stat_type.value}' for slot {self.slot}.")

        # Validate substats
        if len(self.sub_stats) > MAX_SUBSTATS_COUNT:
            raise ValueError(f"Cannot have more than {MAX_SUBSTATS_COUNT} substats.")
        sub_stat_types = set()
        total_sub_rolls = 0
        for i, sub in enumerate(self.sub_stats):
            if not isinstance(sub, SubStatInstance):
                 raise TypeError(f"sub_stats list must contain SubStatInstance objects, found {type(sub)} at index {i}.")
            if sub.stat_type == self.main_stat_type:
                 raise ValueError(f"Substat '{sub.stat_type.value}' cannot be the same as main stat.")
            if sub.stat_type not in POSSIBLE_SUBSTATS:
                 raise ValueError(f"Invalid substat type: '{sub.stat_type.value}'.")
            if sub.stat_type in sub_stat_types:
                 raise ValueError(f"Duplicate substat type found: '{sub.stat_type.value}'.")
            sub_stat_types.add(sub.stat_type)
            if not 0 <= sub.rolls <= MAX_SUBSTAT_ROLLS:
                 raise ValueError(f"Invalid number of rolls ({sub.rolls}) for substat '{sub.stat_type.value}'. Must be 0-{MAX_SUBSTAT_ROLLS}.")
            total_sub_rolls += sub.rolls
        if total_sub_rolls > MAX_SUBSTAT_ROLLS:
            raise ValueError(f"Total substat rolls ({total_sub_rolls}) exceed maximum allowed ({MAX_SUBSTAT_ROLLS}).")
            

        # Could add validation for number of substats/rolls vs level/rarity, but complex
        # It might be better handled when *creating* the disc instance from DB data

    def get_main_stat_value(self) -> float:
        """
        Calculates the value of the main stat based on type, rarity, and level.
        Uses gdl to fetch main stat values.
        If the value for the specific level is not found, attempts to return
        the value for the maximum level for the disc's rarity.
        """
        # 1. Try to get value for the current level from game_data_loader
        value = gdl.get_drive_main_stat_value(self.rarity, self.main_stat_type, self.level)

        if value is None:
             # Value for current level not found, try getting max level value
             max_level_for_rarity = MAX_LEVEL_PER_RARITY.get(self.rarity)
             if max_level_for_rarity is not None:
                 print(f"Info: Main stat value not found for {self.rarity.name} {self.main_stat_type.name} at level {self.level}. "
                       f"Attempting fallback to max level {max_level_for_rarity}.")
                 value = gdl.get_drive_main_stat_value(self.rarity, self.main_stat_type, max_level_for_rarity)

             # If max level value is also None, return 0 as final fallback
             if value is None:
                 print(f"Warning: Max level ({max_level_for_rarity}) main stat value also not found for "
                       f"{self.rarity.name} {self.main_stat_type.name}. Returning 0.")
                 return 0.0

        # Return the found value (either for current level or max level)
        return value

    def get_all_substat_values(self) -> Dict[Stat, float]:
        """Calculates and returns a dictionary of {Stat: value} for all substats."""
        sub_values: Dict[Stat, float] = {}
        for sub in self.sub_stats:
            sub_values[sub.stat_type] = sub.get_value(self.rarity)
        return sub_values

    # --- Potential future method ---
    # def get_total_stats_contribution(self) -> 'Stats': # Assuming a Stats class exists
    #     """Combines main stat and substats into a single Stats object."""
    #     from .stats import Stats # Example import
    #     total_stats = Stats() # Create empty stats object
    #     # Add main stat
    #     main_value = self.get_main_stat_value()
    #     total_stats.add_stat(self.main_stat_type, main_value)
    #     # Add substats
    #     for sub_stat, sub_value in self.get_all_substat_values().items():
    #         total_stats.add_stat(sub_stat, sub_value)
    #     return total_stats