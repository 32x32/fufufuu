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
        # Adding model 'ReportManga'
        db.create_table('report_manga', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('manga', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['manga.Manga'])),
            ('report_type', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('comment', self.gf('django.db.models.fields.TextField')()),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now_add=True)),
        ))
        db.send_create_signal('report', ['ReportManga'])

        # Adding index on 'ReportManga', fields ['manga', 'status']
        db.create_index('report_manga', ['manga_id', 'status'])


    def backwards(self, orm):
        # Removing index on 'ReportManga', fields ['manga', 'status']
        db.delete_index('report_manga', ['manga_id', 'status'])

        # Deleting model 'ReportManga'
        db.delete_table('report_manga')


    models = {
        'account.user': {
            'Meta': {'db_table': "'user'", 'object_name': 'User'},
            'avatar': ('django.db.models.fields.files.FileField', [], {'null': 'True', 'max_length': '255', 'blank': 'True'}),
            'comment_limit': ('django.db.models.fields.IntegerField', [], {'default': '50'}),
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
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'upload_limit': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'manga.manga': {
            'Meta': {'db_table': "'manga'", 'object_name': 'Manga'},
            'category': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'default': "'OTHER'", 'max_length': '20'}),
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'null': 'True', 'to': "orm['tag.Tag']", 'related_name': "'+'", 'blank': 'True'}),
            'collection_part': ('django.db.models.fields.CharField', [], {'null': 'True', 'max_length': '20', 'blank': 'True'}),
            'cover': ('django.db.models.fields.files.FileField', [], {'null': 'True', 'max_length': '255'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'null': 'True', 'to': "orm['account.User']", 'related_name': "'+'", 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'favorite_users': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'to': "orm['account.User']", 'related_name': "'manga_favorites'", 'symmetrical': 'False'}),
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'default': "'en'", 'max_length': '20'}),
            'markdown': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'published_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'default': "'DRAFT'", 'max_length': '20'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'to': "orm['tag.Tag']", 'symmetrical': 'False'}),
            'tank': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'null': 'True', 'to': "orm['tag.Tag']", 'related_name': "'+'", 'blank': 'True'}),
            'tank_chapter': ('django.db.models.fields.CharField', [], {'null': 'True', 'max_length': '20', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'default': "'Untitled'", 'max_length': '100'}),
            'uncensored': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'null': 'True', 'to': "orm['account.User']", 'related_name': "'+'", 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'db_index': 'True', 'auto_now': 'True'})
        },
        'report.reportmanga': {
            'Meta': {'db_table': "'report_manga'", 'object_name': 'ReportManga', 'index_together': "[('manga', 'status')]"},
            'comment': ('django.db.models.fields.TextField', [], {}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manga': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['manga.Manga']"}),
            'report_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'tag.tag': {
            'Meta': {'db_table': "'tag'", 'object_name': 'Tag', 'unique_together': "[('tag_type', 'name')]"},
            'cover': ('django.db.models.fields.files.FileField', [], {'null': 'True', 'max_length': '255', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'null': 'True', 'to': "orm['account.User']", 'related_name': "'+'", 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'tag_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'null': 'True', 'to': "orm['account.User']", 'related_name': "'+'", 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'db_index': 'True', 'auto_now': 'True'})
        }
    }

    complete_apps = ['report']
