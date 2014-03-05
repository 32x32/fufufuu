# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
        ('tag', '0001_initial'),
    )

    def forwards(self, orm):
        # Adding model 'LegacyTank'
        db.create_table('legacy_tank', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tag.Tag'])),
        ))
        db.send_create_signal('legacy', ['LegacyTank'])


    def backwards(self, orm):
        # Deleting model 'LegacyTank'
        db.delete_table('legacy_tank')


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
            'is_moderator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'markdown': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'revision_limit': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'upload_limit': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'})
        },
        'legacy.legacytank': {
            'Meta': {'object_name': 'LegacyTank', 'db_table': "'legacy_tank'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.Tag']"})
        },
        'tag.tag': {
            'Meta': {'object_name': 'Tag', 'unique_together': "[('tag_type', 'name')]", 'db_table': "'tag'"},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'blank': 'True', 'null': 'True', 'related_name': "'+'", 'to': "orm['account.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'tag_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'blank': 'True', 'null': 'True', 'related_name': "'+'", 'to': "orm['account.User']"}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True', 'db_index': 'True'})
        }
    }

    complete_apps = ['legacy']
