import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Type

from .common import Attribute, SkillType

# --- Dataclasses for JSON structure ---

@dataclass
class ScalingData:
    """Represents dmg_scaling or daze_scaling data."""
    step: float = 0.0
    level_1: float = 0.0
    level_16: float = 0.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional['ScalingData']:
        """Creates ScalingData instance from a dictionary."""
        if not isinstance(data, dict):
            return None
        try:
            # Convert string keys "1", "16" to attributes level_1, level_16
            return cls(
                step=float(data.get("step", 0.0)),
                level_1=float(data.get("1", 0.0)),
                level_16=float(data.get("16", 0.0))
            )
        except (ValueError, TypeError):
            # Handle cases where values aren't valid numbers
            print(f"Warning: Could not parse scaling data: {data}")
            return None

    def get_value_at_level(self, level: int) -> float:
        """Calculates the scaling value at a specific level (1-16)."""
        if level <= 1:
            return self.level_1
        if level >= 16:
            return self.level_16
        # Linear interpolation between level 1 and level 16
        calculated_value = self.level_1 + self.step * (level - 1)
        return calculated_value


@dataclass
class MultiplierData:
    """Represents data for a specific hit/multiplier within an ability."""
    dmg_tags: List[str] = field(default_factory=list)
    skill_type: SkillType = SkillType.UNKNOWN
    attribute: Attribute = Attribute.UNKNOWN
    energy_gain: float = 0.0
    decibel_gain: float = 0.0
    anomaly_buildup: float = 0.0
    hit_count: int = 1 # Default to 1 if not specified
    damage_spread: List[float] = field(default_factory=list)
    energy_cost: Optional[int] = None # e.g., for EX skills
    dmg_scaling: Optional[ScalingData] = None
    daze_scaling: Optional[ScalingData] = None
    # description: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional['MultiplierData']:
        """Creates MultiplierData instance from a dictionary."""
        if not isinstance(data, dict):
            return None

        dmg_scaling_data = data.get("dmg_scaling")
        daze_scaling_data = data.get("daze_scaling")

        try:
            return cls(
                dmg_tags=data.get("dmg_tags", []),
                skill_type=SkillType.from_string(data.get("skill_type", "")),
                attribute=Attribute.from_string(data.get("attribute", "")),
                energy_gain=float(data.get("energy_gain", 0.0)),
                decibel_gain=float(data.get("decibel_gain", 0.0)),
                anomaly_buildup=float(data.get("anomaly_buildup", 0.0)),
                hit_count=int(data.get("hit_count", 1)),
                damage_spread=data.get("damage_spread", []),
                energy_cost=int(data.get("energy_cost", 0)),
                dmg_scaling=ScalingData.from_dict(dmg_scaling_data) if dmg_scaling_data else None,
                daze_scaling=ScalingData.from_dict(daze_scaling_data) if daze_scaling_data else None,
                # description=data.get("description")
            )
        except (ValueError, TypeError) as e:
            print(f"Warning: Could not parse multiplier data: {data}. Error: {e}")
            return None


@dataclass
class SkillData:
    """Represents a single skill (e.g., Basic Attack, Ultimate)."""
    name: str
    description: Optional[str] = None
    multipliers: Dict[str, MultiplierData] = field(default_factory=dict)
    other_data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> Optional['SkillData']:
        """Creates SkillData instance from a dictionary."""
        if not isinstance(data, dict):
            return None

        multipliers_dict = {}
        other_data_dict = {}
        desc = data.get("description")

        for key, value in data.items():
            if key == "description":
                continue
            if isinstance(value, dict) and ("dmg_scaling" in value or "daze_scaling" in value):
                multiplier_obj = MultiplierData.from_dict(value)
                if multiplier_obj:
                    multipliers_dict[key] = multiplier_obj
            else:
                other_data_dict[key] = value

        return cls(
            name=name,
            description=desc,
            multipliers=multipliers_dict,
            other_data=other_data_dict
        )

@dataclass
class AgentSkillData:
    """Represents the top-level structure holding all skill data for an agent."""
    core_skills: Dict[str, Any] = field(default_factory=dict)
    skills: Dict[str, SkillData] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional['AgentSkillData']:
        """Creates AgentSkillData instance from the full JSON dictionary."""
        if not isinstance(data, dict):
            return None

        core_skills_data = data.get("Core Skill", {})
        skills_data = data.get("Skills", {})
        parsed_skills = {}

        if isinstance(skills_data, dict):
            for name, ability_dict in skills_data.items():
                ability_obj = SkillData.from_dict(name, ability_dict)
                if ability_obj:
                    parsed_skills[name] = ability_obj

        return cls(
            core_skills=core_skills_data, # Store core_skills as raw dict for now
            skills=parsed_skills
        )