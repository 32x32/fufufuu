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
            ('key_type', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('key_id', self.gf('django.db.models.fields.IntegerField')()),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=255)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('image', ['Image'])

        # Adding unique constraint on 'Image', fields ['key_type', 'key_id']
        db.create_unique('image', ['key_type', 'key_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Image', fields ['key_type', 'key_id']
        db.delete_unique('image', ['key_type', 'key_id'])

        # Deleting model 'Image'
        db.delete_table('image')


    models = {
        'image.image': {
            'Meta': {'db_table': "'image'", 'unique_together': "[('key_type', 'key_id')]", 'object_name': 'Image'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key_id': ('django.db.models.fields.IntegerField', [], {}),
            'key_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['image']