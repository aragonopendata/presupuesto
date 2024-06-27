from django.db import models
from django.core.cache import get_cache
from economic_category import EconomicCategory
from functional_category import FunctionalCategory
from funding_category import FundingCategory
from institutional_category import InstitutionalCategory


class BudgetManager(models.Manager):
    # Return the latest budget for the given entity
    def latest(self, entity_id):
        return self.filter(entity_id=entity_id).order_by('-year')[0]

    # Return a list of years for which we have a budget
    def get_years(self):
        return self.values_list('year', flat=True).distinct().order_by('year')

    # Return the status for all budgets for a given entity
    def get_statuses(self, entity_id):
        result = {}
        for status in self.filter(entity_id=entity_id).values('year', 'status'):
            result[status['year']] = status['status']
        return result

    # Not the most efficient way, but work is ongoing in this area
    def _to_hash(self, items):
        result = {}
        for item in items:
            result[item.uid()] = item.description
        return result

    # Unfortunately institutions id change sometimes over the years, so we need to
    # use id's that are unique along time, not only inside a given budget.
    # (Not too keen on having the object uid polluted with year information all the
    # time, so I keep this here, and in the policies controller, the user of this.)
    def _to_year_tagged_hash(self, items):
        result = {}
        for item in items:
            result[str(item.budget.year) + '/' + item.uid()] = item.description
        return result

    # We need to differentiate between items with the same name in chapters 4 and 7,
    # which have the same structure. We should probably do this during the loading 
    # process, but it's too late now.
    def _get_economic_descriptions(self, items):
        result = {}
        for item in items:
            if item.chapter == '4' or item.chapter == '7':
                result[item.uid()] = item.description + ' (cap. ' + item.chapter + ')'
            else:
                result[item.uid()] = item.description
        return result

    # Get all descriptions available
    def get_all_descriptions(self, entity):
        cache = get_cache('default')
        key = "entity_"+entity.code
        if cache.get(key) == None:
            descriptions = {
                'functional': self._to_hash(FunctionalCategory.objects.filter(budget_id__entity=entity)),
                'income': self._get_economic_descriptions(EconomicCategory.objects.income().filter(budget_id__entity=entity)),
                'expense': self._get_economic_descriptions(EconomicCategory.objects.expenses().filter(budget_id__entity=entity)),
                'funding': self._to_hash(FundingCategory.objects.filter(budget_id__entity=entity)),
                'institutional': self._to_year_tagged_hash(InstitutionalCategory.objects.filter(budget_id__entity=entity))
            }
            cache.set(key, descriptions)
            return descriptions
        else:
            return cache.get(key)


class Budget(models.Model):
    entity = models.ForeignKey('Entity', db_column='entity_id')
    year = models.IntegerField(db_index=True)
    status = models.CharField(max_length=5)     # e.g. DRAFT, 1T, 2T, 3T
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = BudgetManager()

    class Meta:
        app_label = "budget_app"
        db_table = "budgets"

    def __unicode__(self):
        return self.name()

    def name(self):
        return self.entity.name+' '+str(self.year)
