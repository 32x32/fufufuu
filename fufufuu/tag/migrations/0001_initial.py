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
        # Adding model 'Tag'
        db.create_table('tag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now_add=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now=True, db_index=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.User'], related_name='+', blank=True, null=True, on_delete=models.SET_NULL)),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.User'], related_name='+', blank=True, null=True, on_delete=models.SET_NULL)),
            ('tag_type', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=100)),
        ))
        db.send_create_signal('tag', ['Tag'])

        # Adding unique constraint on 'Tag', fields ['tag_type', 'name']
        db.create_unique('tag', ['tag_type', 'name'])

        # Adding model 'TagHistory'
        db.create_table('tag_history', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tag.Tag'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=100)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now_add=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.User'], related_name='+', blank=True, null=True, on_delete=models.SET_NULL)),
        ))
        db.send_create_signal('tag', ['TagHistory'])

        # Adding model 'TagAlias'
        db.create_table('tag_alias', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tag.Tag'])),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now_add=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.User'], related_name='+', blank=True, null=True, on_delete=models.SET_NULL)),
        ))
        db.send_create_signal('tag', ['TagAlias'])

        # Adding unique constraint on 'TagAlias', fields ['tag', 'language', 'name']
        db.create_unique('tag_alias', ['tag_id', 'language', 'name'])

        # Adding model 'TagData'
        db.create_table('tag_data', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now_add=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now=True, db_index=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.User'], related_name='+', blank=True, null=True, on_delete=models.SET_NULL)),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.User'], related_name='+', blank=True, null=True, on_delete=models.SET_NULL)),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tag.Tag'])),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=20)),
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
            ('language', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('markdown', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('html', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('cover', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now_add=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.User'], related_name='+', blank=True, null=True, on_delete=models.SET_NULL)),
        ))
        db.send_create_signal('tag', ['TagDataHistory'])


    def backwards(self, orm):
        # Removing unique constraint on 'TagData', fields ['tag', 'language']
        db.delete_unique('tag_data', ['tag_id', 'language'])

        # Removing unique constraint on 'TagAlias', fields ['tag', 'language', 'name']
        db.delete_unique('tag_alias', ['tag_id', 'language', 'name'])

        # Removing unique constraint on 'Tag', fields ['tag_type', 'name']
        db.delete_unique('tag', ['tag_type', 'name'])

        # Deleting model 'Tag'
        db.delete_table('tag')

        # Deleting model 'TagHistory'
        db.delete_table('tag_history')

        # Deleting model 'TagAlias'
        db.delete_table('tag_alias')

        # Deleting model 'TagData'
        db.delete_table('tag_data')

        # Deleting model 'TagDataHistory'
        db.delete_table('tag_data_history')


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
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'upload_limit': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'tag.tag': {
            'Meta': {'object_name': 'Tag', 'unique_together': "[('tag_type', 'name')]", 'db_table': "'tag'"},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.User']", 'related_name': "'+'", 'blank': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'tag_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.User']", 'related_name': "'+'", 'blank': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True', 'db_index': 'True'})
        },
        'tag.tagalias': {
            'Meta': {'object_name': 'TagAlias', 'unique_together': "[('tag', 'language', 'name')]", 'db_table': "'tag_alias'"},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.User']", 'related_name': "'+'", 'blank': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.Tag']"})
        },
        'tag.tagdata': {
            'Meta': {'object_name': 'TagData', 'unique_together': "[('tag', 'language')]", 'db_table': "'tag_data'"},
            'cover': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.User']", 'related_name': "'+'", 'blank': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'markdown': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.Tag']"}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.User']", 'related_name': "'+'", 'blank': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True', 'db_index': 'True'})
        },
        'tag.tagdatahistory': {
            'Meta': {'object_name': 'TagDataHistory', 'db_table': "'tag_data_history'"},
            'cover': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.User']", 'related_name': "'+'", 'blank': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'markdown': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tag_data': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.TagData']"})
        },
        'tag.taghistory': {
            'Meta': {'object_name': 'TagHistory', 'db_table': "'tag_history'"},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.User']", 'related_name': "'+'", 'blank': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.Tag']"})
        }
    }

    complete_apps = ['tag']
