from django.template.defaultfilters import slugify
from django.db import models


class EconomicCategoriesManager(models.Manager):
    def expenses(self):
        return self.filter(expense=True)

    def income(self):
        return self.filter(expense=False)


class EconomicCategory(models.Model):
    budget = models.ForeignKey('Budget')
    expense = models.BooleanField()
    chapter = models.CharField(max_length=1)
    article = models.CharField(max_length=2, null=True)
    heading = models.CharField(max_length=3, null=True)
    subheading = models.CharField(max_length=6, null=True)
    description = models.CharField(max_length=300)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = EconomicCategoriesManager()

    class Meta:
        app_label = "aragon"
        db_table = "economic_categories"

    # Return the 'budget domain' id, used to uniquely identify a category
    # in a budget
    def uid(self):
        if self.article == None:
            return self.chapter
        elif self.heading == None:
            return self.article
        elif self.subheading == None:
            return self.heading
        return self.subheading

    def slug(self):
        return slugify(self.description)

    def __unicode__(self):
        return self.description
