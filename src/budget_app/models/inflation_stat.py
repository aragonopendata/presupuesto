from django.db import models


class InflationStatManager(models.Manager):
    def get_table(self):
        table = {}
        for stat in self.all():
            table[stat.year] = {
                'inflation': stat.inflation
            }

        # We get raw inflation data from the stats file, we need an index,
        # where the latest year equals 100.
        inflation_index = None
        for year in sorted(table.keys(), reverse=True):
            if inflation_index is None:
                inflation_index = 100        # Most recent year
            else:
                inflation_index = inflation_index / (1 + (table[year+1]['inflation']/100))
            table[year]['inflation_index'] = inflation_index

        return table

    def get_last_year(self):
        return self.order_by('-year').all()[0].year


class InflationStat(models.Model):
    year = models.IntegerField()
    inflation = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = InflationStatManager()

    class Meta:
        app_label = "budget_app"
        db_table = "inflation_stats"

    def __unicode__(self):
        return self.year
