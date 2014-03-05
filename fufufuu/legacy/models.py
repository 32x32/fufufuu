from django.db import models
from fufufuu.tag.models import Tag


class LegacyTank(models.Model):

    tag = models.ForeignKey(Tag)

    class Meta:
        db_table = 'legacy_tank'
