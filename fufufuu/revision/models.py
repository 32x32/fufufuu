import base64
import pickle
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.forms.models import model_to_dict
from fufufuu.account.models import User
from fufufuu.revision.enums import RevisionStatus, RevisionAction


class Revision(models.Model):
    """
    The diff format is as follows:
        diff = {
            'field1': (old_value, new_value),
            'field2': (old_value, new_value),
            ...
        }

    diff_raw is a base64 encoded pickled python dictionary
    """

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    diff_raw = models.TextField()

    messsage = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=RevisionStatus.choices, default=RevisionStatus.PENDING, db_index=True)

    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'revision'
        index_together = [('content_type', 'object_id')]

    def get_diff(self):
        return pickle.loads(base64.b64decode(self.diff_raw.encode('utf-8')))
    def set_diff(self, diff_dict):
        self.diff_raw = base64.b64encode(pickle.dumps(diff_dict)).decode('utf-8')
    diff = property(get_diff, set_diff)

    @classmethod
    def create(cls, old_instance, new_instance, created_by, m2m_data=None):
        """
        IMPORTANT: Revisions must be created before new m2m relationships have
        been saved into the database.
        """

        m2m_data = m2m_data or {}

        assert type(old_instance) == type(new_instance)
        assert old_instance.id == new_instance.id

        field_list = new_instance.revision_field_list

        old_fields = model_to_dict(old_instance, fields=field_list+list(m2m_data.keys()))
        new_fields = model_to_dict(new_instance, fields=field_list)

        diff_dict = {}

        for field in field_list:
            old_value = old_fields[field]
            new_value = new_fields[field]
            if old_value != new_value: diff_dict[field] = (old_value, new_value)

        for field, new_value in m2m_data.items():
            old_value = old_fields[field]
            if set(old_value) != set(new_value): diff_dict[field] = (old_value, new_value)

        if not diff_dict: return None

        revision = cls(content_object=new_instance, created_by=created_by)
        revision.diff = diff_dict
        revision.save()

        return revision

    def revert(self):
        return self._update(0)

    def apply(self):
        return self._update(1)

    def _update(self, pos):
        m2m_data = {}
        obj = self.content_object
        for field, values in self.diff.items():
            field_type = type(obj._meta.get_field(field))
            if field_type == models.ForeignKey:
                setattr(obj, field+'_id', values[pos])
            elif field_type == models.ManyToManyField:
                m2m_data[field] = values[pos]
            else:
                setattr(obj, field, values[pos])
        return obj, m2m_data


class RevisionEvent(models.Model):

    revision = models.ForeignKey(Revision)

    action = models.CharField(max_length=20, choices=RevisionAction.choices)
    old_status = models.CharField(max_length=20, choices=RevisionStatus.choices)
    new_status = models.CharField(max_length=20, choices=RevisionStatus.choices)
    message = models.TextField(blank=True, null=True)

    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'revision_event'
