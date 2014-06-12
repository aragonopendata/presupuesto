from django.db import models
from django.template.defaultfilters import slugify

class EntityManager(models.Manager):
    # This assumes there is only one region, which we know is true for now
    def region(self):
        return self.filter(level='comunidad')[0]

    def counties(self):
        return entiites('comarca')

    def towns(self):
        return entities('municipio')

    def entities(self, level):
        return self.filter(level=level).order_by('name')

    def get_entities_table(self, level):
        table = {}
        for county in self.filter(level=level):
            table[county.name] = {
                'code': county.code,
                'slug': county.slug
            }
        return table

    def search(self, query):
        sql =   "select id, level, name, slug from entities " \
                "where " \
                    "to_tsvector(name) @@ plainto_tsquery(%s) "
        return self.raw(sql, [query,])


class Entity(models.Model):
    code = models.CharField(max_length=10, db_index=True)
    level = models.CharField(max_length=20, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(unique=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = EntityManager()

    class Meta:
        app_label = "aragon"
        db_table = "entities"

    def save(self):
        if not self.id: # Only set the slug when the object is created.
            self.slug = slugify(self.name)
        super(Entity, self).save()

    def __unicode__(self):
        return self.name
