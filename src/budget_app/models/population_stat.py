from django.db import models
from budget_app.models import Entity, InflationStat


class PopulationStatManager(models.Manager):
    def get_entity_table(self, entity):
        table = {}
        stats = self.filter(entity=entity).order_by('year')
        for stat in stats:
            table[stat.year] = stat.population

        # Now populate the returned table up to the latest year, filling in the gaps.
        # We need to do this because population data is often incomplete or not up to date.
        last_year = InflationStat.objects.get_last_year()
        last_valid_population = None
        for year in range(stats[0].year, last_year+3):  # Some extra years to avoid breaking every year
            if year in table:
                last_valid_population = table[year]
            table[year] = last_valid_population
        return table

    def get_level_table(self, level):
        table = {}
        for entity in Entity.objects.entities(level):
            table[entity.name] = self.get_entity_table(entity)
        return table

    def get_last_year(self):
        return self.order_by('-year').all()[0].year


class PopulationStat(models.Model):
    entity = models.ForeignKey('Entity', db_column='entity_id')
    year = models.IntegerField()
    population = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = PopulationStatManager()

    class Meta:
        app_label = "budget_app"
        db_table = "population_stats"

    def __unicode__(self):
        return self.year
