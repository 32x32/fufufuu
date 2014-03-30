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
        # Adding model 'Comment'
        db.create_table('comment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('markdown', self.gf('django.db.models.fields.TextField')()),
            ('html', self.gf('django.db.models.fields.TextField')()),
            ('is_removed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ip_address', self.gf('django.db.models.fields.CharField')(null=True, max_length=200, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(null=True, related_name='+', to=orm['account.User'], on_delete=models.SET_NULL, blank=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('comment', ['Comment'])

        # Adding index on 'Comment', fields ['content_type', 'object_id']
        db.create_index('comment', ['content_type_id', 'object_id'])


    def backwards(self, orm):
        # Removing index on 'Comment', fields ['content_type', 'object_id']
        db.delete_index('comment', ['content_type_id', 'object_id'])

        # Deleting model 'Comment'
        db.delete_table('comment')


    models = {
        'account.user': {
            'Meta': {'db_table': "'user'", 'object_name': 'User'},
            'avatar': ('django.db.models.fields.files.FileField', [], {'null': 'True', 'max_length': '255', 'blank': 'True'}),
            'comment_limit': ('django.db.models.fields.IntegerField', [], {'default': '50'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'edit_limit': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '254', 'blank': 'True'}),
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_moderator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'markdown': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'report_limit': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'upload_limit': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'comment.comment': {
            'Meta': {'db_table': "'comment'", 'object_name': 'Comment', 'index_together': "[('content_type', 'object_id')]"},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'related_name': "'+'", 'to': "orm['account.User']", 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'html': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'null': 'True', 'max_length': '200', 'blank': 'True'}),
            'is_removed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'markdown': ('django.db.models.fields.TextField', [], {}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'contenttypes.contenttype': {
            'Meta': {'db_table': "'django_content_type'", 'object_name': 'ContentType', 'unique_together': "(('app_label', 'model'),)", 'ordering': "('name',)"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['comment']
