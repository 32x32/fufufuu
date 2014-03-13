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
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(db_index=True, blank=True, auto_now=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(on_delete=models.SET_NULL, blank=True, related_name='+', to=orm['account.User'], null=True)),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(on_delete=models.SET_NULL, blank=True, related_name='+', to=orm['account.User'], null=True)),
            ('tag_type', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=100)),
            ('cover', self.gf('django.db.models.fields.files.FileField')(null=True, blank=True, max_length=255)),
        ))
        db.send_create_signal('tag', ['Tag'])

        # Adding unique constraint on 'Tag', fields ['tag_type', 'name']
        db.create_unique('tag', ['tag_type', 'name'])

        # Adding model 'TagAlias'
        db.create_table('tag_alias', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tag.Tag'])),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now_add=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(on_delete=models.SET_NULL, blank=True, related_name='+', to=orm['account.User'], null=True)),
        ))
        db.send_create_signal('tag', ['TagAlias'])

        # Adding unique constraint on 'TagAlias', fields ['tag', 'language', 'name']
        db.create_unique('tag_alias', ['tag_id', 'language', 'name'])

        # Adding model 'TagData'
        db.create_table('tag_data', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now_add=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(db_index=True, blank=True, auto_now=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(on_delete=models.SET_NULL, blank=True, related_name='+', to=orm['account.User'], null=True)),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(on_delete=models.SET_NULL, blank=True, related_name='+', to=orm['account.User'], null=True)),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tag.Tag'])),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('markdown', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('html', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('tag', ['TagData'])

        # Adding unique constraint on 'TagData', fields ['tag', 'language']
        db.create_unique('tag_data', ['tag_id', 'language'])


    def backwards(self, orm):
        # Removing unique constraint on 'TagData', fields ['tag', 'language']
        db.delete_unique('tag_data', ['tag_id', 'language'])

        # Removing unique constraint on 'TagAlias', fields ['tag', 'language', 'name']
        db.delete_unique('tag_alias', ['tag_id', 'language', 'name'])

        # Removing unique constraint on 'Tag', fields ['tag_type', 'name']
        db.delete_unique('tag', ['tag_type', 'name'])

        # Deleting model 'Tag'
        db.delete_table('tag')

        # Deleting model 'TagAlias'
        db.delete_table('tag_alias')

        # Deleting model 'TagData'
        db.delete_table('tag_data')


    models = {
        'account.user': {
            'Meta': {'object_name': 'User', 'db_table': "'user'"},
            'avatar': ('django.db.models.fields.files.FileField', [], {'null': 'True', 'blank': 'True', 'max_length': '255'}),
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
        'tag.tag': {
            'Meta': {'unique_together': "[('tag_type', 'name')]", 'object_name': 'Tag', 'db_table': "'tag'"},
            'cover': ('django.db.models.fields.files.FileField', [], {'null': 'True', 'blank': 'True', 'max_length': '255'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'blank': 'True', 'related_name': "'+'", 'to': "orm['account.User']", 'null': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'tag_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'blank': 'True', 'related_name': "'+'", 'to': "orm['account.User']", 'null': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'blank': 'True', 'auto_now': 'True'})
        },
        'tag.tagalias': {
            'Meta': {'unique_together': "[('tag', 'language', 'name')]", 'object_name': 'TagAlias', 'db_table': "'tag_alias'"},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'blank': 'True', 'related_name': "'+'", 'to': "orm['account.User']", 'null': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.Tag']"})
        },
        'tag.tagdata': {
            'Meta': {'unique_together': "[('tag', 'language')]", 'object_name': 'TagData', 'db_table': "'tag_data'"},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'blank': 'True', 'related_name': "'+'", 'to': "orm['account.User']", 'null': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'markdown': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.Tag']"}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'blank': 'True', 'related_name': "'+'", 'to': "orm['account.User']", 'null': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'blank': 'True', 'auto_now': 'True'})
        }
    }

    complete_apps = ['tag']
