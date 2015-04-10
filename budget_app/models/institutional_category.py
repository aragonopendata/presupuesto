from django.db import models


class InstitutionalCategoriesManager(models.Manager):
    pass


class InstitutionalCategory(models.Model):
    budget = models.ForeignKey('Budget')
    institution = models.CharField(max_length=5)
    section = models.CharField(max_length=8, null=True)
    department = models.CharField(max_length=11, null=True)
    description = models.CharField(max_length=200)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = InstitutionalCategoriesManager()

    class Meta:
        app_label = "budget_app"
        db_table = "institutional_categories"

    # Return the 'budget domain' id, used to uniquely identify a category
    # in a budget
    def uid(self):
        if self.section == None:
            return self.institution
        elif self.department == None:
            return self.section
        return self.department

    def __unicode__(self):
        return self.description
