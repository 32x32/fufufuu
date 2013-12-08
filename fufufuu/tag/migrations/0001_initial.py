# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Tag'
        db.create_table('tag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tag_type', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=20)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now_add=True)),
        ))
        db.send_create_signal('tag', ['Tag'])

        # Adding model 'TagData'
        db.create_table('tag_data', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now_add=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(db_index=True, auto_now=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(null=True, related_name='+', on_delete=models.SET_NULL, blank=True, to=orm['account.User'])),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(null=True, related_name='+', on_delete=models.SET_NULL, blank=True, to=orm['account.User'])),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tag.Tag'])),
            ('language', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=20)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=100)),
            ('markdown', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('html', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('cover', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True)),
        ))
        db.send_create_signal('tag', ['TagData'])

        # Adding unique constraint on 'TagData', fields ['tag', 'language']
        db.create_unique('tag_data', ['tag_id', 'language'])

        # Adding model 'TagDataHistory'
        db.create_table('tag_data_history', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tag_data', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tag.TagData'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=100)),
            ('markdown', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('html', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('cover', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now_add=True)),
        ))
        db.send_create_signal('tag', ['TagDataHistory'])

        # Adding model 'TagAlias'
        db.create_table('tag_alias', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now_add=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(db_index=True, auto_now=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(null=True, related_name='+', on_delete=models.SET_NULL, blank=True, to=orm['account.User'])),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(null=True, related_name='+', on_delete=models.SET_NULL, blank=True, to=orm['account.User'])),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tag.TagData'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=100)),
        ))
        db.send_create_signal('tag', ['TagAlias'])


    def backwards(self, orm):
        # Removing unique constraint on 'TagData', fields ['tag', 'language']
        db.delete_unique('tag_data', ['tag_id', 'language'])

        # Deleting model 'Tag'
        db.delete_table('tag')

        # Deleting model 'TagData'
        db.delete_table('tag_data')

        # Deleting model 'TagDataHistory'
        db.delete_table('tag_data_history')

        # Deleting model 'TagAlias'
        db.delete_table('tag_alias')


    models = {
        'account.user': {
            'Meta': {'object_name': 'User', 'db_table': "'user'"},
            'avatar': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True', 'null': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '254', 'blank': 'True'}),
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'markdown': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'tag.tag': {
            'Meta': {'object_name': 'Tag', 'db_table': "'tag'"},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag_type': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20'})
        },
        'tag.tagalias': {
            'Meta': {'object_name': 'TagAlias', 'db_table': "'tag_alias'"},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'related_name': "'+'", 'on_delete': 'models.SET_NULL', 'blank': 'True', 'to': "orm['account.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.TagData']"}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'related_name': "'+'", 'on_delete': 'models.SET_NULL', 'blank': 'True', 'to': "orm['account.User']"}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'auto_now': 'True', 'blank': 'True'})
        },
        'tag.tagdata': {
            'Meta': {'object_name': 'TagData', 'unique_together': "(('tag', 'language'),)", 'db_table': "'tag_data'"},
            'cover': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'related_name': "'+'", 'on_delete': 'models.SET_NULL', 'blank': 'True', 'to': "orm['account.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20'}),
            'markdown': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.Tag']"}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'related_name': "'+'", 'on_delete': 'models.SET_NULL', 'blank': 'True', 'to': "orm['account.User']"}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'auto_now': 'True', 'blank': 'True'})
        },
        'tag.tagdatahistory': {
            'Meta': {'object_name': 'TagDataHistory', 'db_table': "'tag_data_history'"},
            'cover': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'markdown': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'tag_data': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.TagData']"})
        }
    }

    complete_apps = ['tag']