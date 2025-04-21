# core/agent_data.py

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from .common import Attribute, Faction, Rarity, Stat, AttackType, Specialty


@dataclass
class AgentInfo:
    """Represents the 'info' block for an agent."""
    full_name: Optional[str] = None
    gender: Optional[str] = None
    height: Optional[str] = None
    birthday: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentInfo':
        """Creates AgentInfo instance from a dictionary."""
        if not isinstance(data, dict):
            return cls() # Return default empty instance if data is not dict

        return cls(
            full_name=data.get("full_name"),
            gender=data.get("gender"),
            height=data.get("height"),
            birthday=data.get("birthday")
        )

@dataclass
class AgentBaseStats:
    """Represents the 'base_stats' block for an agent."""
    hp: int = 0
    atk: int = 0
    defense: int = 0 # Renamed from base_def
    impact: int = 0
    anomaly_mastery: int = 0
    anomaly_proficiency: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentBaseStats':
        """Creates AgentBaseStats instance from a dictionary."""
        if not isinstance(data, dict):
            return cls()

        try:
            # Rename keys like 'base_hp' to 'hp' during parsing
            return cls(
                hp=int(data.get("base_hp", 0)),
                atk=int(data.get("base_atk", 0)),
                defense=int(data.get("base_def", 0)),
                impact=int(data.get("base_impact", 0)),
                anomaly_mastery=int(data.get("base_anomaly_mastery", 0)),
                anomaly_proficiency=int(data.get("base_anomaly_proficiency", 0))
            )
        except (ValueError, TypeError) as e:
            print(f"Warning: Could not parse base stats data: {data}. Error: {e}")
            return cls() # Return default on error

@dataclass
class AgentCoreStat:
    """Represents the 'core_stat' block for an agent."""
    stat: Stat = Stat.UNKNOWN
    value: float = 0.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentCoreStat':
        """Creates AgentCoreStat instance from a dictionary."""
        if not isinstance(data, dict):
            return cls()

        try:
            return cls(
                stat=Stat.from_string(data.get("stat", "")),
                value=float(data.get("value", 0.0))
            )
        except (ValueError, TypeError) as e:
            print(f"Warning: Could not parse core stat data: {data}. Error: {e}")
            return cls() # Return default on error

@dataclass
class AgentData:
    """Represents all data for a single agent."""
    name: str # The key from the top-level JSON (e.g., "Ellen")
    attribute: Attribute = Attribute.UNKNOWN
    specialty: Specialty = Specialty.UNKNOWN
    faction: Faction = Faction.UNKNOWN
    type: List[AttackType] = field(default_factory=list)
    rarity: Rarity = Rarity.UNKNOWN
    info: AgentInfo = field(default_factory=AgentInfo)
    base_stats: AgentBaseStats = field(default_factory=AgentBaseStats)
    core_stat: AgentCoreStat = field(default_factory=AgentCoreStat)
    # Add field for skills if needed later, e.g.:
    # skills: Optional[AgentSkillData] = None

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> Optional['AgentData']:
        """Creates AgentData instance from the agent's dictionary."""
        if not isinstance(data, dict):
            return None

        return cls(
            name=name,
            attribute=Attribute.from_string(data.get("attribute", "")),
            specialty=Specialty.from_string(data.get("specialty", "")),
            faction=Faction.from_string(data.get("faction", "")),
            type=[AttackType.from_string(_type) for _type in data.get("type", [])],
            rarity=Rarity.from_string(data.get("rarity", "")),
            info=AgentInfo.from_dict(data.get("info", {})),
            base_stats=AgentBaseStats.from_dict(data.get("base_stats", {})),
            core_stat=AgentCoreStat.from_dict(data.get("core_stat", {}))
        )