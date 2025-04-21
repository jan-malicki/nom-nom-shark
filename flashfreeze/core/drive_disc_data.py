# core/drive_disc_data.py

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

# Assuming common.py is in the same directory (core/) or accessible
# Adjust import path if needed
from .common import Stat


@dataclass
class DriveDiscSetBonus:
    """Represents the data associated with a single set bonus effect (either 2pc or 4pc)."""
    piece_count: int # 2 or 4
    # --- Fields primarily for 2-piece bonus ---
    stat: Optional[Stat] = None
    value: Optional[float] = None # The value associated with the stat
    # --- Fields primarily for 4-piece bonus ---
    description: Optional[str] = None
    # Dictionary holding values for description placeholders (e.g., {"atk": 9, "duration": 6})
    values: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, piece_count: int, data: Optional[Dict[str, Any]]) -> Optional['DriveDiscSetBonus']:
        """
        Creates DriveDiscSetBonus instance from a dictionary, parsing fields
        based on the expected piece_count (2 or 4).
        """
        if not isinstance(data, dict):
            return None # No data provided for this piece count

        stat_obj = None
        value_val = None
        desc_val = None
        values_dict = {}

        # Parse fields based on whether we expect a 2pc or 4pc bonus structure
        if piece_count == 2:
            try:
                stat_str = data.get("stat", "")
                stat_obj = Stat.from_string(stat_str) if stat_str else Stat.UNKNOWN
                value_val = float(data.get("value")) if "value" in data else None
            except (ValueError, TypeError) as e:
                print(f"Warning: Could not parse 2-piece bonus data: {data}. Error: {e}")
                stat_obj = Stat.UNKNOWN
                value_val = None
        elif piece_count == 4:
            desc_val = data.get("description")
            values_dict = data.get("values", {})
            if not isinstance(values_dict, dict):
                print(f"Warning: 'values' field in 4-piece bonus is not a dictionary: {values_dict}")
                values_dict = {}
        else:
            print(f"Warning: Invalid piece_count '{piece_count}' passed to DriveDiscSetBonus.from_dict.")
            return None

        # Only create object if some data was actually parsed
        if stat_obj or value_val is not None or desc_val or values_dict:
             return cls(
                 piece_count=piece_count, # Store piece_count again
                 stat=stat_obj,
                 value=value_val,
                 description=desc_val,
                 values=values_dict
             )
        else:
             return None


    def get_value_keys(self) -> List[str]:
        """
        Returns a list of the value keys available in the bonus effect values dict.
        Only relevant for 4-piece bonuses.
        Example: ['atk', 'duration'] for Woodpecker Electro 4-piece.
        """
        # Check piece_count before accessing values
        if self.piece_count == 4 and isinstance(self.values, dict):
            return list(self.values.keys())
        return []

    def get_formatted_description(self) -> Optional[str]:
        """
        Returns the bonus description string with placeholders formatted
        using the 'values' dictionary. Only relevant for 4-piece bonuses.

        Returns:
            The formatted description string, or the original description if
            formatting fails or required data is missing. Returns None if
            the original description is None.
        """
        if self.description is None:
            return None
        # Check piece_count before formatting
        if self.piece_count != 4 or not isinstance(self.values, dict) or not self.values:
            return self.description

        try:
            formatted_desc = self.description
            for key, value in self.values.items():
                 placeholder = "{" + key + "}"
                 formatted_desc = formatted_desc.replace(placeholder, str(value))
            return formatted_desc
        except (KeyError, ValueError, TypeError) as e:
            print(f"Warning: Could not format description for 4-piece bonus. Error: {e}")
            return self.description


@dataclass
class DriveDiscSetData:
    """Represents all data for a single Drive Disc set."""
    name: str # The key from the top-level JSON (e.g., "Woodpecker Electro")
    bonus_2pc: Optional[DriveDiscSetBonus] = None
    bonus_4pc: Optional[DriveDiscSetBonus] = None

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> Optional['DriveDiscSetData']:
        """Creates DriveDiscSetData instance from the set's dictionary."""
        if not isinstance(data, dict):
            return None

        bonus_2pc_obj = DriveDiscSetBonus.from_dict(2, data.get("2-piece"))
        bonus_4pc_obj = DriveDiscSetBonus.from_dict(4, data.get("4-piece"))

        if bonus_2pc_obj or bonus_4pc_obj:
            return cls(
                name=name,
                bonus_2pc=bonus_2pc_obj,
                bonus_4pc=bonus_4pc_obj
            )
        else:
            return None