from django.db import models
from django.conf import settings


class BudgetItemManager(models.Manager):
    def each_denormalized(self, additional_constraints=None, additional_arguments=None):
        sql = \
            "select " \
                "fc.policy, fc.function, fc.programme, " \
                "ec.chapter, ec.article, ec.heading, ec.subheading, " \
                "ic.institution, ic.department, " \
                "fdc.source, fdc.fund, "\
                "i.id, i.item_number, i.description, i.expense, i.actual, i.amount, " \
                "b.year, " \
                "e.name " \
            "from " \
                "budget_items i, " \
                "functional_categories fc, " \
                "institutional_categories ic, " \
                "economic_categories ec, " \
                "funding_categories fdc, " \
                "budgets b, " \
                "entities e " \
            "where " \
                "i.functional_category_id = fc.id and " \
                "i.institutional_category_id = ic.id and " \
                "i.economic_category_id = ec.id and " \
                "i.funding_category_id = fdc.id and " \
                "i.budget_id = b.id and " \
                "b.entity_id = e.id"

        if additional_constraints:
            sql += " and " + additional_constraints

        return self.raw(sql, additional_arguments)

    # Do a full-text search in the database. Note we ignore execution data, as it doesn't
    # add anything new to the budget descriptions.
    def search(self, query, year, page):
        sql = "select " \
            "b.year, " \
            "e.name, e.level, " \
            "i.id, i.description, i.amount, i.expense, " \
            "ec.article, ec.heading, ec.subheading, " \
            "ic.institution, ic.department, " \
            "fc.policy, fc.programme " \
          "from " \
            "budget_items i, " \
            "budgets b, " \
            "entities e, " \
            "functional_categories fc, " \
            "economic_categories ec, " \
            "institutional_categories ic " \
          "where " \
            "i.budget_id = fc.budget_id and " \
            "i.budget_id = b.id and " \
            "b.entity_id = e.id and " \
            "i.actual = false and " \
            "i.functional_category_id = fc.id and " \
            "i.institutional_category_id = ic.id and " \
            "i.economic_category_id = ec.id and " \
            "to_tsvector('"+settings.SEARCH_CONFIG+"',i.description) @@ plainto_tsquery('"+settings.SEARCH_CONFIG+"',%s)"
        if year:
            sql += " and b.year='%s'" % year
        sql += " order by i.amount desc"
        return self.raw(sql, (query, ))


class BudgetItem(models.Model):
    budget = models.ForeignKey('Budget')
    actual = models.BooleanField()
    expense = models.BooleanField()
    item_number = models.CharField(max_length=3)
    description = models.CharField(max_length=512)
    amount = models.BigIntegerField()
    economic_category = models.ForeignKey('EconomicCategory', db_column='economic_category_id')
    functional_category = models.ForeignKey('FunctionalCategory', db_column='functional_category_id')
    funding_category = models.ForeignKey('FundingCategory', db_column='funding_category_id')
    institutional_category = models.ForeignKey('InstitutionalCategory', db_column='institutional_category_id')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = BudgetItemManager()

    class Meta:
        app_label = "budget_app"
        db_table = "budget_items"

    # Return a budget id unique across all years, so we can match them later
    # with the descriptions. Important note: this won't work in a normal budget
    # item, it expects a denormalized record.
    # CAREFUL: An 'item number' plus an economic category doesn't make a line
    # unique: you need the institution too! (I.e. you basically need the whole
    # line. In this case we can skip the functional category, since we filter
    # along that dimension)
    def uid(self):
        # XXX: The subheading call originally assumed the values do exist; not true anymore 
        # with smaller entities. I'm working around it for now, partially, but I haven't 
        # thought fully about the implications of all this.
        department = getattr(self, 'department') if getattr(self, 'department') else ''
        subheading = getattr(self, 'subheading') if getattr(self, 'subheading') else (getattr(self, 'heading') if getattr(self, 'heading') else (getattr(self, 'article') if getattr(self, 'article') else getattr(self, 'chapter')))
        item_number = getattr(self, 'item_number') if getattr(self, 'item_number') else ''
        return str(getattr(self, 'year')) + '/' + \
                department + '/' + \
                subheading + '/' + \
                item_number

    def year(self):
        return self.budget.year

    def programme(self):
        return self.functional_category.programme

    # Whether an item is a financial expense (i.e. paying debt, mostly) or income (i.e. new debt).
    # Only works on a denormalized record.
    def is_financial(self):
        return getattr(self, 'chapter') == '8' or getattr(self, 'chapter') == '9'

    def __unicode__(self):
        return self.description
