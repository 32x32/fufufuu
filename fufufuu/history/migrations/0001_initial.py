# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
        ('account', '0001_initial'),
    )

    def forwards(self, orm):
        # Adding model 'History'
        db.create_table('history', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now_add=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(on_delete=models.SET_NULL, blank=True, to=orm['account.User'], null=True)),
        ))
        db.send_create_signal('history', ['History'])

        # Adding index on 'History', fields ['content_type', 'object_id']
        db.create_index('history', ['content_type_id', 'object_id'])

        # Adding model 'HistoryField'
        db.create_table('history_field', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('history', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['history.History'])),
            ('field', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('old_value', self.gf('django.db.models.fields.TextField')()),
            ('new_value', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('history', ['HistoryField'])


    def backwards(self, orm):
        # Removing index on 'History', fields ['content_type', 'object_id']
        db.delete_index('history', ['content_type_id', 'object_id'])

        # Deleting model 'History'
        db.delete_table('history')

        # Deleting model 'HistoryField'
        db.delete_table('history_field')


    models = {
        'account.user': {
            'Meta': {'object_name': 'User', 'db_table': "'user'"},
            'avatar': ('django.db.models.fields.files.FileField', [], {'blank': 'True', 'max_length': '100', 'null': 'True'}),
            'comment_limit': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'blank': 'True', 'max_length': '254'}),
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'markdown': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'upload_limit': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'object_name': 'ContentType', 'unique_together': "(('app_label', 'model'),)", 'ordering': "('name',)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'history.history': {
            'Meta': {'object_name': 'History', 'index_together': "[('content_type', 'object_id')]", 'db_table': "'history'"},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'blank': 'True', 'to': "orm['account.User']", 'null': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'history.historyfield': {
            'Meta': {'object_name': 'HistoryField', 'db_table': "'history_field'"},
            'field': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'history': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['history.History']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_value': ('django.db.models.fields.TextField', [], {}),
            'old_value': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['history']
