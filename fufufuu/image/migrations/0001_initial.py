# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Image'
        db.create_table('image', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('transformation', self.gf('django.db.models.fields.TextField')()),
            ('source', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('output', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('image', ['Image'])


    def backwards(self, orm):
        # Deleting model 'Image'
        db.delete_table('image')


    models = {
        'image.image': {
            'Meta': {'db_table': "'image'", 'object_name': 'Image'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'output': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'source': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'transformation': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['image']