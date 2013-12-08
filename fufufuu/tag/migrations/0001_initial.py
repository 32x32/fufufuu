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
            ('tag_type', self.gf('django.db.models.fields.CharField')(max_length=20, db_index=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('tag', ['Tag'])

        # Adding model 'TagData'
        db.create_table('tag_data', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(db_index=True, blank=True, auto_now=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(null=True, blank=True, related_name='+', to=orm['account.User'], on_delete=models.SET_NULL)),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(null=True, blank=True, related_name='+', to=orm['account.User'], on_delete=models.SET_NULL)),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tag.Tag'])),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=20, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=100)),
            ('markdown', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('html', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('cover', self.gf('django.db.models.fields.files.FileField')(null=True, max_length=100)),
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
            ('cover', self.gf('django.db.models.fields.files.FileField')(null=True, max_length=100)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('tag', ['TagDataHistory'])

        # Adding model 'TagAlias'
        db.create_table('tag_alias', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(db_index=True, blank=True, auto_now=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(null=True, blank=True, related_name='+', to=orm['account.User'], on_delete=models.SET_NULL)),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(null=True, blank=True, related_name='+', to=orm['account.User'], on_delete=models.SET_NULL)),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tag.TagData'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
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
            'Meta': {'db_table': "'user'", 'object_name': 'User'},
            'avatar': ('django.db.models.fields.files.FileField', [], {'null': 'True', 'max_length': '100', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '254', 'blank': 'True'}),
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'markdown': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'})
        },
        'tag.tag': {
            'Meta': {'db_table': "'tag'", 'object_name': 'Tag'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_index': 'True'})
        },
        'tag.tagalias': {
            'Meta': {'db_table': "'tag_alias'", 'object_name': 'TagAlias'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'blank': 'True', 'related_name': "'+'", 'to': "orm['account.User']", 'on_delete': 'models.SET_NULL'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.TagData']"}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'blank': 'True', 'related_name': "'+'", 'to': "orm['account.User']", 'on_delete': 'models.SET_NULL'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'blank': 'True', 'auto_now': 'True'})
        },
        'tag.tagdata': {
            'Meta': {'db_table': "'tag_data'", 'unique_together': "(('tag', 'language'),)", 'object_name': 'TagData'},
            'cover': ('django.db.models.fields.files.FileField', [], {'null': 'True', 'max_length': '100'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'blank': 'True', 'related_name': "'+'", 'to': "orm['account.User']", 'on_delete': 'models.SET_NULL'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_index': 'True'}),
            'markdown': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.Tag']"}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'blank': 'True', 'related_name': "'+'", 'to': "orm['account.User']", 'on_delete': 'models.SET_NULL'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'blank': 'True', 'auto_now': 'True'})
        },
        'tag.tagdatahistory': {
            'Meta': {'db_table': "'tag_data_history'", 'object_name': 'TagDataHistory'},
            'cover': ('django.db.models.fields.files.FileField', [], {'null': 'True', 'max_length': '100'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {}),
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'markdown': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'tag_data': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.TagData']"})
        }
    }

    complete_apps = ['tag']
