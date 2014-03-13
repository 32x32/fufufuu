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
        # Adding model 'Revision'
        db.create_table('revision', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('diff_raw', self.gf('django.db.models.fields.TextField')()),
            ('messsage', self.gf('django.db.models.fields.TextField')(blank=True, null=True)),
            ('status', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=20, default='PENDING')),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.User'], blank=True, on_delete=models.SET_NULL, null=True)),
        ))
        db.send_create_signal('revision', ['Revision'])

        # Adding index on 'Revision', fields ['content_type', 'object_id']
        db.create_index('revision', ['content_type_id', 'object_id'])

        # Adding model 'RevisionEvent'
        db.create_table('revision_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('revision', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['revision.Revision'])),
            ('action', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('old_status', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('new_status', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('message', self.gf('django.db.models.fields.TextField')(blank=True, null=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.User'], blank=True, on_delete=models.SET_NULL, null=True)),
        ))
        db.send_create_signal('revision', ['RevisionEvent'])


    def backwards(self, orm):
        # Removing index on 'Revision', fields ['content_type', 'object_id']
        db.delete_index('revision', ['content_type_id', 'object_id'])

        # Deleting model 'Revision'
        db.delete_table('revision')

        # Deleting model 'RevisionEvent'
        db.delete_table('revision_event')


    models = {
        'account.user': {
            'Meta': {'db_table': "'user'", 'object_name': 'User'},
            'avatar': ('django.db.models.fields.files.FileField', [], {'blank': 'True', 'null': 'True', 'max_length': '255'}),
            'comment_limit': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
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
        'contenttypes.contenttype': {
            'Meta': {'db_table': "'django_content_type'", 'unique_together': "(('app_label', 'model'),)", 'ordering': "('name',)", 'object_name': 'ContentType'},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'revision.revision': {
            'Meta': {'index_together': "[('content_type', 'object_id')]", 'db_table': "'revision'", 'object_name': 'Revision'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.User']", 'blank': 'True', 'on_delete': 'models.SET_NULL', 'null': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'diff_raw': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'messsage': ('django.db.models.fields.TextField', [], {'blank': 'True', 'null': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'default': "'PENDING'"})
        },
        'revision.revisionevent': {
            'Meta': {'db_table': "'revision_event'", 'object_name': 'RevisionEvent'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.User']", 'blank': 'True', 'on_delete': 'models.SET_NULL', 'null': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'blank': 'True', 'null': 'True'}),
            'new_status': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'old_status': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'revision': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['revision.Revision']"})
        }
    }

    complete_apps = ['revision']
