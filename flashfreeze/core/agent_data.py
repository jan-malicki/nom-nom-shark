# core/agent_data.py

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from flashfreeze.core.drive_disc_data import DriveDisc
from flashfreeze.core.drive_disc_set_data import DriveDiscSetData
from flashfreeze.core.skill_data import AgentSkillData
from flashfreeze.core.w_engine_data import WEngine

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
    defense: int = 0
    impact: int = 0
    anomaly_mastery: int = 0
    anomaly_proficiency: int = 0
    pen_ratio: float = 0.0
    energy_regen: float = 0.0
    energy_limit: int = 0
    crit_rate: float = 0.0
    crit_dmg: float = 0.0

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
                anomaly_proficiency=int(data.get("base_anomaly_proficiency", 0)),
                pen_ratio=float(data.get("base_pen_ratio", 0.0)),
                energy_regen=float(data.get("base_energy_regen", 1.2)), # Default to 1.2 if not specified
                energy_limit=int(data.get("base_energy_limit", 120)), # Default to 100 if not specified
                crit_rate=float(data.get("base_crit_rate", 5.0)), # Default to 5 if not specified
                crit_dmg=float(data.get("base_crit_dmg", 50.0)), # Default to 50 if not specified
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
    skills: Optional[AgentSkillData] = None

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
    
@dataclass
class AgentBonusStats:
    """Represents the total pre-combat stats of an agent."""
    hp: int = 0
    hp_percent: float = 0.0
    atk: int = 0
    atk_percent: float = 0.0
    defense: int = 0
    def_percent: float = 0.0
    impact: int = 0
    impact_percent: float = 0.0
    crit_rate: float = 0.0
    crit_dmg: float = 0.0
    anomaly_mastery: int = 0
    anomaly_mastery_percent: float = 0.0
    anomaly_proficiency: int = 0
    pen_ratio: float = 0.0
    pen: int = 0
    energy_regen: float = 0.0
    energy_regen_percent: float = 0.0
    energy_generation_rate: float = 0.0
    energy_limit: int = 0
    physical_dmg: float = 0.0
    fire_dmg: float = 0.0
    ice_dmg: float = 0.0
    electric_dmg: float = 0.0
    ether_dmg: float = 0.0

    def add_stat(self, stat: Stat, value: float):
        """Adds a value to the specified stat in this AgentStats instance."""
        match stat:
            case Stat.HP:
                self.hp += int(value)
            case Stat.HP_PERCENT:
                self.hp_percent += value
            case Stat.ATK:
                self.atk += int(value)
            case Stat.ATK_PERCENT:
                self.atk_percent += value
            case Stat.DEF:
                self.defense += int(value)
            case Stat.DEF_PERCENT:
                self.def_percent += value
            case Stat.IMPACT:
                self.impact += int(value)
            case Stat.IMPACT_PERCENT:
                self.impact_percent += value
            case Stat.CRIT_RATE:
                self.crit_rate += value
            case Stat.CRIT_DMG:
                self.crit_dmg += value
            case Stat.ANOMALY_MASTERY:
                self.anomaly_mastery += int(value)
            case Stat.ANOMALY_MASTERY_PERCENT:
                self.anomaly_mastery_percent += value
            case Stat.ANOMALY_PROFICIENCY:
                self.anomaly_proficiency += int(value)
            case Stat.PEN_RATIO:
                self.pen_ratio += value
            case Stat.PEN:
                self.pen += int(value)
            case Stat.ENERGY_REGEN:
                self.energy_regen += value
            case Stat.ENERGY_REGEN_PERCENT:
                self.energy_regen_percent += value
            case Stat.ENERGY_GENERATION_RATE:
                self.energy_generation_rate += value
            case Stat.ENERGY_LIMIT:
                self.energy_limit += int(value)
            case Stat.PHYSICAL_DMG:
                self.physical_dmg += value
            case Stat.FIRE_DMG:
                self.fire_dmg += value
            case Stat.ICE_DMG:
                self.ice_dmg += value
            case Stat.ELECTRIC_DMG:
                self.electric_dmg += value
            case Stat.ETHER_DMG:
                self.ether_dmg += value
            case _:
                print(f"Warning: Unsupported stat type {stat}")

@dataclass
class AgentTotalStats:
    """Represents the total pre-combat stats of an agent."""
    hp: int = 0
    atk: int = 0
    defense: int = 0
    impact: int = 0
    crit_rate: float = 0.0
    crit_dmg: float = 0.0
    anomaly_mastery: int = 0
    anomaly_proficiency: int = 0
    pen_ratio: float = 0.0
    pen: int = 0
    energy_regen: float = 0.0
    energy_limit: int = 0
    physical_dmg: float = 0.0
    fire_dmg: float = 0.0
    ice_dmg: float = 0.0
    electric_dmg: float = 0.0
    ether_dmg: float = 0.0

    @classmethod
    def from_base_and_bonus(cls, base_stats: AgentBaseStats, bonus_stats: AgentBonusStats) -> 'AgentTotalStats':
        """Calculates total stats by combining base and bonus stats."""
        return cls(
            hp=base_stats.hp * (1 + bonus_stats.hp_percent/100) + bonus_stats.hp,
            atk=base_stats.atk * (1 + bonus_stats.atk_percent/100) + bonus_stats.atk,
            defense=base_stats.defense * (1 + bonus_stats.def_percent/100) + bonus_stats.defense,
            impact=base_stats.impact * (1 + bonus_stats.impact_percent/100) + bonus_stats.impact,
            crit_rate=base_stats.crit_rate + bonus_stats.crit_rate,
            crit_dmg=base_stats.crit_dmg + bonus_stats.crit_dmg,
            anomaly_mastery=base_stats.anomaly_mastery * (1 + bonus_stats.anomaly_mastery_percent/100) + bonus_stats.anomaly_mastery,
            anomaly_proficiency=base_stats.anomaly_proficiency + bonus_stats.anomaly_proficiency,
            pen_ratio=base_stats.pen_ratio + bonus_stats.pen_ratio,
            pen=bonus_stats.pen,  # Only from bonuses
            energy_regen=base_stats.energy_regen * (1 + bonus_stats.energy_regen_percent/100) + bonus_stats.energy_regen,
            energy_limit=base_stats.energy_limit + bonus_stats.energy_limit,
            physical_dmg=bonus_stats.physical_dmg,  # Only from bonuses
            fire_dmg=bonus_stats.fire_dmg,
            ice_dmg=bonus_stats.ice_dmg,
            electric_dmg=bonus_stats.electric_dmg,
            ether_dmg=bonus_stats.ether_dmg,
        )

@dataclass
class AgentSkillLevels:
    """Represents the skill levels for an agent."""
    skill_levels: Dict[str, int] = field(default_factory=dict)

    def get_skill_level(self, skill_name: str) -> int:
        """Returns the level of a specific skill."""
        return self.skill_levels.get(skill_name, 0)

@dataclass
class Agent:
    """Represents an agent instance in a specific combat/calculation state."""
    # Static base data for the agent
    base_agent_data: AgentData

    # Current level (can override base data if needed, but usually fixed)
    level: int = 1
    promotion: int = 0 # 0-5 (0 = base, 5 = max promotion)
    mindscape: int = 0 # 0-6 (0 = base, 6 = max mindscape)

    # Equipped Gear
    w_engine: Optional[WEngine] = None
    drive_discs: Dict[int, DriveDisc] = field(default_factory=dict) # slot -> disc

    # Skill Levels (Placeholder - needs definition based on game mechanics)
    # Maps skill name (or ID) to its level (e.g., 1-10?)
    skill_levels: Dict[str, int] = field(default_factory=dict)

    # --- Caching ---
    _cached_total_stats: Optional[AgentTotalStats] = field(default=None, init=False, repr=False)

    def __post_init__(self):
        self.level = max(1, min(self.level, 60))
        self.promotion = max(0, min(self.promotion, 5))
        self.mindscape = max(0, min(self.mindscape, 6))

        # Validate level based on promotion
        min_level = self.promotion * 10
        max_level = min_level + 10
        if not (min_level <= self.level <= max_level):
            print(f"Warning: Level {self.level} is out of range for promotion {self.promotion}. Adjusting.")
            self.level = max(min_level, min(self.level, max_level))

        # Recalculate total stats on initialization
        self.recalculate_total_stats()

    def get_active_set_counts(self) -> Dict[DriveDiscSetData, int]:
        """Counts how many pieces of each set are equipped."""
        set_counts: Dict[DriveDiscSetData, int] = {}
        for disc in self.drive_discs.values():
            set_data = disc.set_data
            set_counts[set_data] = set_counts.get(set_data, 0) + 1
        return set_counts

    def get_bonus_stats(self) -> AgentBonusStats:
        """Internal method to collect all bonus stats from the Agent's gear."""
        # --- Step 0: Create an AgentBonusStats object to accumulate bonuses ---
        bonus_stats = AgentBonusStats()

        # --- Step 1: W-Engine Advanced Stat ---
        if self.w_engine:
            adv_stat_info = self.w_engine.get_advanced_stat()
            if adv_stat_info:
                adv_s_type, adv_s_value = adv_stat_info
                bonus_stats.add_stat(adv_s_type, adv_s_value)

        # --- Step 2: Drive Discs Main & Substats ---
        for slot, disc in self.drive_discs.items():
            # Main Stat
            main_s_type = disc.main_stat_type
            main_s_value = disc.get_main_stat_value() # Uses level/rarity
            bonus_stats.add_stat(main_s_type, main_s_value)

            # Substats
            substats = disc.get_all_substat_values() # Uses rarity/rolls
            for sub_s_type, sub_s_value in substats.items():
                 bonus_stats.add_stat(sub_s_type, sub_s_value)

        # --- Step 3: Drive Disc 2-Piece Set Bonuses ---
        set_counts = self.get_active_set_counts()
        for set_data, count in set_counts.items():
            if count >= 2:
                if set_data and set_data.bonus_2pc and set_data.bonus_2pc.simple_stat:
                    bonus_stat = set_data.bonus_2pc.simple_stat
                    bonus_value = set_data.bonus_2pc.value
                    if bonus_stat and bonus_value is not None:
                         bonus_stats.add_stat(bonus_stat, bonus_value)

        return bonus_stats

    def recalculate_total_stats(self):
        """Recalculates the total stats by combining base and bonus stats."""
        bonus_stats = self.get_bonus_stats()
        self._cached_total_stats = AgentTotalStats.from_base_and_bonus(
            self.base_agent_data.base_stats, bonus_stats
        )

    @property
    def total_stats(self) -> AgentTotalStats:
        """Returns the total stats of the agent, recalculating if necessary."""
        if self._cached_total_stats is None:
            self.recalculate_total_stats()
        return self._cached_total_stats

    def __setattr__(self, name, value):
        """Override setattr to recalculate total stats when properties change."""
        super().__setattr__(name, value)
        if name in {"level", "promotion", "mindscape", "w_engine", "drive_discs", "skill_levels"}:
            self.recalculate_total_stats()