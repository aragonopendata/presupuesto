from django.db import models


class GlossaryTermManager(models.Manager):
    def search(self, query):
        sql = "select id, title, description from glossary_terms "

        # If no query is passed (i.e. we're showing the glossary page),
        # return all the terms.
        if query and query != '':
            sql += "where " \
                "to_tsvector(title) @@ plainto_tsquery(%s) or " \
                "to_tsvector(description) @@ plainto_tsquery(%s) "

        sql += "order by title asc"
        return self.raw(sql, [query, query])


class GlossaryTerm(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=2000)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = GlossaryTermManager()

    class Meta:
        app_label = "aragon"
        db_table = "glossary_terms"

    def __unicode__(self):
        return self.title
