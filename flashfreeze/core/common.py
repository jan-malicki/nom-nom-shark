from enum import Enum

class StringEnum(Enum):
    @classmethod
    def from_string(cls, value: str) -> 'StringEnum':
        """Safely create enum from string value."""
        for item in cls:
            if item.value.lower() == value.lower():
                return item
        return cls.UNKNOWN

class Attribute(StringEnum):
    PHYSICAL = "Physical"
    FIRE = "Fire"
    ICE = "Ice"
    ELECTRIC = "Electric"
    ETHER = "Ether"
    UNKNOWN = "Unknown"

class Rarity(StringEnum):
    C = "C"
    B = "B"
    A = "A"
    S = "S"
    UNKNOWN = "Unknown"

class Stat(StringEnum):
    HP = "HP"
    ATK = "ATK"
    DEF = "DEF"
    HP_PERCENT = "HP%"
    ATK_PERCENT = "ATK%"
    DEF_PERCENT = "DEF%"
    IMPACT = "Impact"
    CRIT_RATE = "CRIT Rate"
    CRIT_DMG = "CRIT DMG"
    ANOMALY_MASTERY = "Anomaly Mastery"
    ANOMALY_PROFICIENCY = "Anomaly Proficiency"
    PEN_RATIO = "PEN Ratio"
    PEN = "PEN"
    ENERGY_REGEN = "Energy Regen"
    ENERGY_GENERATION_RATE = "Energy Generation Rate"
    PHYSICAL_DMG = "Physical DMG"
    FIRE_DMG = "Fire DMG"
    ICE_DMG = "Ice DMG"
    ELECTRIC_DMG = "Electric DMG"
    ETHER_DMG = "Ether DMG"
    UNKNOWN = "Unknown"

class Faction(StringEnum):
    CUNNING_HARES = "Cunning Hares"
    BELOBOG_HEAVY_INDUSTRIES = "Belobog Heavy Industries"
    VICTORIA_HOUSEKEEPING_CO = "Victoria Housekeeping Co."
    CRIMINAL_INVESTYIGATION_SPECIAL_RESPONSE_TEAM = "Criminal Investigation Special Response Team"
    SONS_OF_CALYDON = "Sons of Calydon"
    OBOL_SQUAD = "Obol Squad"
    HOLLOW_SPECIAL_OPERATIONS_SECTION_6 = "Hollow Special Operations Section 6"
    STARS_OF_LYRA = "Stars of Lyra"
    DEFENSE_FORCE_SILVER_SQUAD = "Defense Force - Silver Squad"
    MOCKINGBIRD = "Mockingbird"
    UNKNOWN = "Unknown"

class SkillType(StringEnum):
    BASIC_ATTACK = "Basic Attack"
    DODGE = "Dodge"
    SPECIAL_ATTACK = "Special Attack"
    ASSIST = "Assist"
    CHAIN_ATTACK = "Chain Attack"
    UNKNOWN = "Unknown"

class AttackType(StringEnum):
    STRIKE = "Strike"
    SLASH = "Slash"
    PIERCE = "Pierce"
    UNKNOWN = "Unknown"

class Specialty(StringEnum):
    ANOMALY = "Anomaly"
    ATTACK = "Attack"
    DEFENSE = "Defense"
    STUN = "Stun"
    SUPPORT = "Support"
    UNKNOWN = "Unknown"