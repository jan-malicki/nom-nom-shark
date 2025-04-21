# core/w_engine_data.py

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from .common import Rarity, Stat, Specialty

@dataclass
class WEngineSubStat:
    """Represents the sub_stat block for a W-Engine."""
    stat: Stat = Stat.UNKNOWN
    value: float = 0.0

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional['WEngineSubStat']:
        """Creates WEngineSubStat instance from a dictionary."""
        if not isinstance(data, dict):
            return None # Return None if sub_stat block is missing or not a dict

        try:
            return cls(
                stat=Stat.from_string(data.get("stat", "")),
                value=float(data.get("value", 0.0))
            )
        except (ValueError, TypeError) as e:
            print(f"Warning: Could not parse W-Engine sub stat data: {data}. Error: {e}")
            return None # Return None on parsing error


@dataclass
class WEnginePassive:
    """Represents the passive block for a W-Engine."""
    name: Optional[str] = None
    description: Optional[str] = None
    values: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional['WEnginePassive']:
        """Creates WEnginePassive instance from a dictionary."""
        if not isinstance(data, dict):
            return None # Return None if passive block is missing or not a dict

        return cls(
            name=data.get("name"),
            description=data.get("description"),
            values=data.get("values", {}) # Default to empty dict if missing
        )

    def get_passive_value(self, phase: int, value_key: str) -> Optional[Any]:
        """
        Helper method to get a specific passive value for a given phase/refinement (1-5).
        Example: get_passive_value(phase=1, value_key='physical_dmg') -> 20
        """
        if not 1 <= phase <= 5:
            print(f"Warning: Phase must be between 1 and 5, got {phase}.")
            return None
        phase_key = f"phase_{phase}"
        phase_data = self.values.get(phase_key)
        if isinstance(phase_data, dict):
            return phase_data.get(value_key)
        return None

    def get_value_keys(self) -> List[str]:
        """
        Returns a list of the value keys available in the passive scaling.
        Assumes all phases have the same keys and uses phase_1 to determine them.
        Example: ['physical_dmg', 'back_dmg'] for Steel Cushion.
        """
        if not self.values:
            return [] # Return empty list if no values data exists

        phase_1_data = self.values.get("phase_1")
        if isinstance(phase_1_data, dict):
            return list(phase_1_data.keys())
        else:
            # Fallback or warning if phase_1 data is missing/invalid
            print(f"Warning: Could not determine value keys from phase_1 data for passive '{self.name}'.")
            return []

    def get_formatted_description(self, phase: int) -> Optional[str]:
        """
        Returns the passive description string with placeholders formatted
        using values from the specified phase (1-5).

        Args:
            phase: The refinement phase (1-5) to use for values.

        Returns:
            The formatted description string, or the original description if
            formatting fails or required data is missing. Returns None if
            the original description is None.
        """
        if self.description is None:
            return None # No description to format

        if not 1 <= phase <= 5:
            print(f"Warning: Phase must be between 1 and 5 for formatting, got {phase}.")
            return self.description # Return original description if phase is invalid

        phase_key = f"phase_{phase}"
        phase_data = self.values.get(phase_key)

        if not isinstance(phase_data, dict):
            # Return original description if phase data is missing or not a dict
            return self.description

        try:
            # Using a loop and replace for robustness against missing keys:
            formatted_desc = self.description
            for key, value in phase_data.items():
                 placeholder = "{" + key + "}" # Construct placeholder like {physical_dmg}
                 # Convert value to string for replacement, handle potential formatting needs
                 formatted_desc = formatted_desc.replace(placeholder, str(value))
            return formatted_desc
            # Alternative using str.format(**kwargs) - might raise KeyError if description
            # contains placeholders not present in phase_data keys.
            # return self.description.format(**phase_data)
        except (KeyError, ValueError, TypeError) as e:
            # Handle potential errors during formatting (e.g., mismatched keys)
            print(f"Warning: Could not format description for passive '{self.name}' phase {phase}. Error: {e}")
            return self.description # Return original description on error


@dataclass
class WEngineData:
    """Represents all data for a single W-Engine."""
    name: str # The key from the top-level JSON (e.g., "Steel Cushion")
    specialty: Specialty = Specialty.UNKNOWN
    rarity: Rarity = Rarity.UNKNOWN
    base_atk: int = 0
    sub_stat: Optional[WEngineSubStat] = None
    passive: Optional[WEnginePassive] = None
    # Add other fields if they exist

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> Optional['WEngineData']:
        """Creates WEngineData instance from the W-Engine's dictionary."""
        if not isinstance(data, dict):
            return None

        # Handle base_atk conversion from string
        base_atk_val = 0
        base_atk_raw = data.get("base_atk")
        if base_atk_raw is not None:
            try:
                base_atk_val = int(base_atk_raw)
            except (ValueError, TypeError):
                print(f"Warning: Could not convert base_atk '{base_atk_raw}' to int for W-Engine '{name}'.")

        return cls(
            name=name,
            specialty=Specialty.from_string(data.get("specialty")),
            rarity=Rarity.from_string(data.get("rarity", "")),
            base_atk=base_atk_val,
            # Parse nested objects using their respective from_dict methods
            sub_stat=WEngineSubStat.from_dict(data.get("sub_stat")), # Pass the sub-dict directly
            passive=WEnginePassive.from_dict(data.get("passive")) # Pass the sub-dict directly
        )