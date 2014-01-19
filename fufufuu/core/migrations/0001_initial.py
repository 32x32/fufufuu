# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DeletedFile'
        db.create_table('core_deletedfile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('delete_after', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 1, 20, 0, 0))),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('core', ['DeletedFile'])


    def backwards(self, orm):
        # Deleting model 'DeletedFile'
        db.delete_table('core_deletedfile')


    models = {
        'core.deletedfile': {
            'Meta': {'object_name': 'DeletedFile'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'delete_after': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 1, 20, 0, 0)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        }
    }

    complete_apps = ['core']