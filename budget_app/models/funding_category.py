from django.db import models


class FundingCategoriesManager(models.Manager):
    pass


class FundingCategory(models.Model):
    budget = models.ForeignKey('Budget')
    expense = models.BooleanField()
    source = models.CharField(max_length=1)
    fund_class = models.CharField(max_length=2, null=True)
    fund = models.CharField(max_length=5, null=True)
    description = models.CharField(max_length=200)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = FundingCategoriesManager()

    class Meta:
        app_label = "budget_app"
        db_table = "funding_categories"

    # Return the 'budget domain' id, used to uniquely identify a category
    # in a budget
    def uid(self):
        if self.fund_class == None:
            return self.source
        elif self.fund == None:
            return self.fund_class
        return self.fund

    def __unicode__(self):
        return self.description
