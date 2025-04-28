import pytest
from flashfreeze.core.common import Stat, Attribute, Specialty, Faction, Rarity, SkillType, AttackType

from flashfreeze.core.agent_data import (
    AgentInfo,
    AgentBaseStats,
    AgentCoreStat,
    AgentData,
    AgentBonusStats,
    AgentTotalStats,
    Agent,
)


def test_agent_info_from_dict():
    data = {
        "full_name": "Ellen",
        "gender": "Female",
        "height": "170cm",
        "birthday": "01-01",
    }
    agent_info = AgentInfo.from_dict(data)
    assert agent_info.full_name == "Ellen"
    assert agent_info.gender == "Female"
    assert agent_info.height == "170cm"
    assert agent_info.birthday == "01-01"


def test_agent_base_stats_from_dict():
    data = {
        "base_hp": 1000,
        "base_atk": 200,
        "base_def": 150,
        "base_crit_dmg": 75.0,
    }
    base_stats = AgentBaseStats.from_dict(data)
    assert base_stats.hp == 1000
    assert base_stats.atk == 200
    assert base_stats.defense == 150
    assert base_stats.crit_rate == 5.0  # Default value
    assert base_stats.crit_dmg == 75.0


def test_agent_core_stat_from_dict():
    data = {"stat": "ATK", "value": 25.0}
    core_stat = AgentCoreStat.from_dict(data)
    assert core_stat.stat == Stat.ATK
    assert core_stat.value == 25.0


def test_agent_data_from_dict():
    data = {
        "attribute": "Ice",
        "specialty": "Attack",
        "faction": "Victoria Housekeeping Co.",
        "type": ["Slash"],
        "rarity": "S",
        "info": {
            "full_name": "Ellen Joe",
            "gender": "Female",
            "height": "161",
            "birthday": "January 4"
        },
        "base_stats": {
            "base_hp": 7673,
            "base_atk": 938,
            "base_def": 606,
            "base_impact": 93,
            "base_anomaly_mastery": 94,
            "base_anomaly_proficiency": 93
        },
        "core_stat": {
            "stat": "CRIT Rate",
            "value": 4.8
        }
    }
    agent_data = AgentData.from_dict("Ellen", data)
    assert agent_data.name == "Ellen"
    assert agent_data.attribute == Attribute.ICE
    assert agent_data.specialty == Specialty.ATTACK
    assert agent_data.faction == Faction.VICTORIA_HOUSEKEEPING_CO
    assert agent_data.type == [AttackType.SLASH]
    assert agent_data.rarity == Rarity.S
    assert agent_data.info.full_name == "Ellen Joe"
    assert agent_data.info.gender == "Female"
    assert agent_data.info.height == "161"
    assert agent_data.info.birthday == "January 4"
    assert agent_data.base_stats.hp == 7673
    assert agent_data.base_stats.atk == 938
    assert agent_data.base_stats.defense == 606
    assert agent_data.base_stats.impact == 93
    assert agent_data.base_stats.anomaly_mastery == 94
    assert agent_data.base_stats.anomaly_proficiency == 93
    assert agent_data.core_stat.stat == Stat.CRIT_RATE
    assert agent_data.core_stat.value == 4.8


def test_agent_bonus_stats_add_stat():
    bonus_stats = AgentBonusStats()
    bonus_stats.add_stat(Stat.HP, 500)
    bonus_stats.add_stat(Stat.ATK_PERCENT, 10.0)
    assert bonus_stats.hp == 500
    assert bonus_stats.atk_percent == 10.0


def test_agent_total_stats_from_base_and_bonus():
    base_stats = AgentBaseStats(hp=1000, atk=200, defense=150)
    bonus_stats = AgentBonusStats(hp=500, atk_percent=10.0, def_percent=20.0)
    total_stats = AgentTotalStats.from_base_and_bonus(base_stats, bonus_stats)
    assert total_stats.hp == 1500
    assert total_stats.atk == 220
    assert total_stats.defense == 180


def test_agent_initialization():
    base_stats = AgentBaseStats(hp=1000, atk=200, defense=150)
    core_stat = AgentCoreStat(stat=Stat.ATK, value=25.0)
    agent_data = AgentData(
        name="Ellen",
        base_stats=base_stats,
        core_stat=core_stat,
    )
    agent = Agent(base_agent_data=agent_data, level=15, promotion=1)
    assert agent.level == 15
    assert agent.promotion == 1
    assert agent.total_stats.hp == 1000  # Base stats only for now


def test_agent_recalculate_total_stats():
    base_stats = AgentBaseStats(hp=1000, atk=200, defense=150, crit_rate=5.0)
    core_stat = AgentCoreStat(stat=Stat.CRIT_RATE, value=4.8)
    agent_data = AgentData(
        name="Ellen",
        base_stats=base_stats,
        core_stat=core_stat,
    )
    agent = Agent(base_agent_data=agent_data, level=15, promotion=1)
    agent.skill_levels[SkillType.CORE_SKILL] = 3
    agent.recalculate_total_stats()
    # Recalculate twice to ensure core stat only applies once
    agent.recalculate_total_stats()
    assert agent.total_stats.atk == 225  # Includes core stat bonus
    assert agent.total_stats.crit_rate == pytest.approx(14.6)