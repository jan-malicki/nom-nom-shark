# core/drive_disc_logic.py

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set

from .common import Stat, Rarity
from .drive_disc_data import DriveDiscSetData # To link equipped disc to its set bonus info
# Import game_data_loader to fetch main/sub stat values from JSON
# Assuming it's accessible, adjust path as needed
from .. import game_data_loader as gdl # Example: if loader is one level up

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
        Requires lookup tables for base values.
        """
        # 1. Get base value from lookup table (JSON loaded via gdl)
        # Example: base_value = gdl.get_drive_substat_base_value(rarity, self.stat_type)
        # Placeholder - replace with actual data loading
        base_value = self._get_placeholder_substat_base_value(rarity, self.stat_type)
        if base_value is None:
            return 0.0

        # 2. Calculate final value: base * (rolls + 1)
        # Clamp rolls just in case (shouldn't exceed MAX_SUBSTAT_ROLLS)
        actual_rolls = min(self.rolls, MAX_SUBSTAT_ROLLS)
        final_value = base_value * (actual_rolls + 1)

        return final_value

    def _get_placeholder_substat_base_value(self, rarity: Rarity, stat_type: Stat) -> Optional[float]:
        """Placeholder for loading substat base values from JSON via gdl."""
        # --- Replace this with actual gdl call ---
        # Example structure for drive_disc_sub_stats.json:
        # { "S": {"HP": 250, "ATK%": 0.04, ...}, "A": {...}, "B": {...} }
        print(f"Placeholder: Fetching base value for {rarity.name} {stat_type.name}")
        # Dummy values for demonstration
        dummy_bases = {
            Rarity.S: {Stat.HP: 254, Stat.ATK: 17, Stat.DEF: 17, Stat.HP_PERCENT: 0.043, Stat.ATK_PERCENT: 0.043, Stat.DEF_PERCENT: 0.054, Stat.PEN: 17, Stat.CRIT_RATE: 0.032, Stat.CRIT_DMG: 0.065, Stat.ANOMALY_PROFICIENCY: 19},
            Rarity.A: {Stat.HP: 200, Stat.ATK: 13, Stat.DEF: 13, Stat.HP_PERCENT: 0.034, Stat.ATK_PERCENT: 0.034, Stat.DEF_PERCENT: 0.043, Stat.PEN: 13, Stat.CRIT_RATE: 0.026, Stat.CRIT_DMG: 0.052, Stat.ANOMALY_PROFICIENCY: 15},
            Rarity.B: {Stat.HP: 150, Stat.ATK: 10, Stat.DEF: 10, Stat.HP_PERCENT: 0.026, Stat.ATK_PERCENT: 0.026, Stat.DEF_PERCENT: 0.032, Stat.PEN: 10, Stat.CRIT_RATE: 0.019, Stat.CRIT_DMG: 0.039, Stat.ANOMALY_PROFICIENCY: 11},
        }
        if rarity in dummy_bases and stat_type in dummy_bases[rarity]:
            return dummy_bases[rarity][stat_type]
        return None
        # --- End of placeholder ---


@dataclass
class EquippedDriveDisc:
    """Represents a specific Drive Disc instance equipped by an agent."""
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
             raise ValueError(f"Invalid main stat '{self.main_stat_type.name}' for slot {self.slot}.")

        # Validate substats
        if len(self.sub_stats) > MAX_SUBSTATS_COUNT:
            raise ValueError(f"Cannot have more than {MAX_SUBSTATS_COUNT} substats.")
        sub_stat_types = set()
        for i, sub in enumerate(self.sub_stats):
            if not isinstance(sub, SubStatInstance):
                 raise TypeError(f"sub_stats list must contain SubStatInstance objects, found {type(sub)} at index {i}.")
            if sub.stat_type == self.main_stat_type:
                 raise ValueError(f"Substat '{sub.stat_type.name}' cannot be the same as main stat.")
            if sub.stat_type not in POSSIBLE_SUBSTATS:
                 raise ValueError(f"Invalid substat type: '{sub.stat_type.name}'.")
            if sub.stat_type in sub_stat_types:
                 raise ValueError(f"Duplicate substat type found: '{sub.stat_type.name}'.")
            sub_stat_types.add(sub.stat_type)
            if not 0 <= sub.rolls <= MAX_SUBSTAT_ROLLS:
                 raise ValueError(f"Invalid number of rolls ({sub.rolls}) for substat '{sub.stat_type.name}'. Must be 0-{MAX_SUBSTAT_ROLLS}.")

        # Could add validation for number of substats/rolls vs level/rarity, but complex
        # It might be better handled when *creating* the disc instance from DB data

    def get_main_stat_value(self) -> float:
        """
        Calculates the value of the main stat based on type, rarity, and level.
        Requires lookup tables for main stat scaling.
        """
        # 1. Get scaling data from lookup table (JSON loaded via gdl)
        # Example: value = gdl.get_drive_main_stat_value(self.rarity, self.main_stat_type, self.level)
        # Placeholder - replace with actual data loading
        value = self._get_placeholder_main_stat_value()
        return value if value is not None else 0.0

    def _get_placeholder_main_stat_value(self) -> Optional[float]:
         """Placeholder for loading main stat values from JSON via gdl."""
         # --- Replace this with actual gdl call ---
         # Example structure for drive_disc_main_stats.json:
         # { "S": { "HP%": {"0": 0.07, "1": ..., "15": 0.466}, "ATK%": {...}, ...}, "A": {...}, "B": {...} }
         print(f"Placeholder: Fetching main stat value for {self.rarity.name} {self.main_stat_type.name} at level {self.level}")
         # Dummy values for demonstration - very simplified
         dummy_main_stats = {
             Rarity.S: {Stat.HP_PERCENT: 0.466, Stat.ATK_PERCENT: 0.466, Stat.CRIT_RATE: 0.324, Stat.HP: 4780, Stat.ATK: 311, Stat.DEF: 389},
             Rarity.A: {Stat.HP_PERCENT: 0.373, Stat.ATK_PERCENT: 0.373, Stat.CRIT_RATE: 0.259, Stat.HP: 3824, Stat.ATK: 249, Stat.DEF: 311},
             Rarity.B: {Stat.HP_PERCENT: 0.280, Stat.ATK_PERCENT: 0.280, Stat.CRIT_RATE: 0.194, Stat.HP: 2868, Stat.ATK: 187, Stat.DEF: 233},
         }
         # This placeholder only returns max value, real implementation needs level lookup
         if self.rarity in dummy_main_stats and self.main_stat_type in dummy_main_stats[self.rarity]:
             # Crude scaling based on level for placeholder
             max_val = dummy_main_stats[self.rarity][self.main_stat_type]
             max_lvl = MAX_LEVEL_PER_RARITY.get(self.rarity, 1)
             return max_val * (self.level / max_lvl) if max_lvl > 0 else 0.0
         return None
         # --- End of placeholder ---

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

