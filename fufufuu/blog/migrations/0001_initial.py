# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BlogEntry'
        db.create_table('blog_entry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=200)),
            ('markdown', self.gf('django.db.models.fields.TextField')()),
            ('html', self.gf('django.db.models.fields.TextField')()),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, on_delete=models.SET_NULL, null=True, to=orm['account.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now_add=True)),
        ))
        db.send_create_signal('blog', ['BlogEntry'])


    def backwards(self, orm):
        # Deleting model 'BlogEntry'
        db.delete_table('blog_entry')


    models = {
        'account.user': {
            'Meta': {'db_table': "'user'", 'object_name': 'User'},
            'avatar': ('django.db.models.fields.files.FileField', [], {'blank': 'True', 'max_length': '255', 'null': 'True'}),
            'comment_limit': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'edit_limit': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'email': ('django.db.models.fields.EmailField', [], {'blank': 'True', 'max_length': '254'}),
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_moderator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'markdown': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'report_limit': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'report_weight': ('django.db.models.fields.DecimalField', [], {'decimal_places': '10', 'max_digits': '19', 'default': '10'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'upload_limit': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'blog.blogentry': {
            'Meta': {'db_table': "'blog_entry'", 'object_name': 'BlogEntry'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'on_delete': 'models.SET_NULL', 'null': 'True', 'to': "orm['account.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'html': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'markdown': ('django.db.models.fields.TextField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['blog']