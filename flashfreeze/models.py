from django.db import models

class StatsMixin(models.Model):
    """ Abstract base model for reusable stat fields """
    atk = models.FloatField(default=0.0)
    hp = models.FloatField(default=0.0)
    defense = models.FloatField(default=0.0)
    crit_rate = models.FloatField(default=0.0)
    crit_dmg = models.FloatField(default=0.0)
    pen_ratio = models.FloatField(default=0.0)
    anomaly_mastery = models.FloatField(default=0.0)
    anomaly_proficiency = models.FloatField(default=0.0)
    impact = models.FloatField(default=0.0)
    # ... add other common stats from your Stats class outline

    # Elemental bonuses can be tricky. Simple approach:
    physical_dmg_bonus = models.FloatField(default=0.0)
    fire_dmg_bonus = models.FloatField(default=0.0)
    ice_dmg_bonus = models.FloatField(default=0.0)
    electric_dmg_bonus = models.FloatField(default=0.0)
    ether_dmg_bonus = models.FloatField(default=0.0)

    # Or use JSONField for more flexibility (requires PostgreSQL)
    # from django.db.models import JSONField
    # elemental_dmg_bonus = JSONField(default=dict) # e.g., {'Physical': 0.10, ...}
    # skill_specific_dmg_bonus = JSONField(default=dict)

    class Meta:
        abstract = True # Makes this a mixin, doesn't create a DB table
