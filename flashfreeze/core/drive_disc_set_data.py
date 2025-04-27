# core/drive_disc_set_data.py

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

# Assuming common.py is in the same directory (core/) or accessible
# Adjust import path if needed
from .common import Stat


@dataclass
class DriveDisc2PieceBonus:
    """Represents the data associated with a 2-piece set bonus effect."""
    simple_stat: Optional[Stat] = None
    complex_stat: Optional[str] = None
    value: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional['DriveDisc2PieceBonus']:
        """Creates DriveDisc2PieceBonus instance from a dictionary."""
        if not isinstance(data, dict):
            return None

        try:
            stat_str = data.get("stat", "")
            stat_obj = Stat.from_string(stat_str) if stat_str else None
            value_val = float(data.get("value")) if "value" in data else None

            if stat_obj is not None and stat_obj != Stat.UNKNOWN:
                return cls(simple_stat=stat_obj, value=value_val)
            else:
                return cls(complex_stat=stat_str, value=value_val)
        except (ValueError, TypeError) as e:
            print(f"Warning: Could not parse 2-piece bonus data: {data}. Error: {e}")
            return cls


@dataclass
class DriveDisc4PieceBonus:
    """Represents the data associated with a 4-piece set bonus effect."""
    description: Optional[str] = None
    values: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional['DriveDisc4PieceBonus']:
        """Creates DriveDisc4PieceBonus instance from a dictionary."""
        if not isinstance(data, dict):
            return None

        desc_val = data.get("description")
        values_dict = data.get("values", {})
        if not isinstance(values_dict, dict):
            print(f"Warning: 'values' field in 4-piece bonus is not a dictionary: {values_dict}")
            values_dict = {}

        return cls(description=desc_val, values=values_dict)

    def get_value_keys(self) -> List[str]:
        """Returns a list of the value keys available in the bonus effect values dict."""
        if isinstance(self.values, dict):
            return list(self.values.keys())
        return []

    def get_formatted_description(self) -> Optional[str]:
        """
        Returns the bonus description string with placeholders formatted
        using the 'values' dictionary.
        """
        if self.description is None:
            return None

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
    bonus_2pc: Optional[DriveDisc2PieceBonus] = None
    bonus_4pc: Optional[DriveDisc4PieceBonus] = None

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> Optional['DriveDiscSetData']:
        """Creates DriveDiscSetData instance from the set's dictionary."""
        if not isinstance(data, dict):
            return None

        bonus_2pc_obj = DriveDisc2PieceBonus.from_dict(data.get("2-piece"))
        bonus_4pc_obj = DriveDisc4PieceBonus.from_dict(data.get("4-piece"))

        if bonus_2pc_obj or bonus_4pc_obj:
            return cls(
                name=name,
                bonus_2pc=bonus_2pc_obj,
                bonus_4pc=bonus_4pc_obj
            )
        else:
            return None