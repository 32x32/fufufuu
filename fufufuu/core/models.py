from django.db import models
from fufufuu.account.models import User


class BaseAuditableModel(models.Model):

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True, db_index=True)

    created_by = models.ForeignKey(User, null=True, blank=True, related_name='+', on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(User, null=True, blank=True, related_name='+', on_delete=models.SET_NULL)

    class Meta:
        abstract = True

    def save(self, updated_by, *args, **kwargs):
        self.updated_by = updated_by
        if not self.created_by:
            self.created_by = updated_by
        super().save(*args, **kwargs)
