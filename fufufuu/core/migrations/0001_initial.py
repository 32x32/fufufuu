# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DeletedFile'
        db.create_table('deleted_file', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('delete_after', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 3, 17, 0, 0))),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now_add=True)),
        ))
        db.send_create_signal('core', ['DeletedFile'])

        # Adding model 'SiteSetting'
        db.create_table('site_setting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('val', self.gf('django.db.models.fields.TextField')(blank=True, null=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now=True)),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(on_delete=models.SET_NULL, blank=True, null=True, to=orm['account.User'])),
        ))
        db.send_create_signal('core', ['SiteSetting'])


    def backwards(self, orm):
        # Deleting model 'DeletedFile'
        db.delete_table('deleted_file')

        # Deleting model 'SiteSetting'
        db.delete_table('site_setting')


    models = {
        'account.user': {
            'Meta': {'object_name': 'User', 'db_table': "'user'"},
            'avatar': ('django.db.models.fields.files.FileField', [], {'blank': 'True', 'null': 'True', 'max_length': '255'}),
            'comment_limit': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'blank': 'True', 'max_length': '254'}),
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_moderator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'markdown': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'revision_limit': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'upload_limit': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'core.deletedfile': {
            'Meta': {'object_name': 'DeletedFile', 'db_table': "'deleted_file'"},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'delete_after': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 17, 0, 0)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
        'core.sitesetting': {
            'Meta': {'object_name': 'SiteSetting', 'db_table': "'site_setting'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'blank': 'True', 'null': 'True', 'to': "orm['account.User']"}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'val': ('django.db.models.fields.TextField', [], {'blank': 'True', 'null': 'True'})
        }
    }

    complete_apps = ['core']