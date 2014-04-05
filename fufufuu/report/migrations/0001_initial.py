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
        # Adding model 'ReportMangaResolution'
        db.create_table('report_manga_resolution', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('manga', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['manga.Manga'])),
            ('removed', self.gf('django.db.models.fields.BooleanField')()),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True, null=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now_add=True)),
        ))
        db.send_create_signal('report', ['ReportMangaResolution'])

        # Adding model 'ReportManga'
        db.create_table('report_manga', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('manga', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['manga.Manga'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='OPEN', max_length=20)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('weight', self.gf('django.db.models.fields.DecimalField')(max_digits=19, decimal_places=10)),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True, null=True)),
            ('ip_address', self.gf('django.db.models.fields.CharField')(blank=True, null=True, max_length=200)),
            ('quality', self.gf('django.db.models.fields.CharField')(default='UNKNOWN', max_length=20)),
            ('resolution', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, to=orm['report.ReportMangaResolution'], null=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, to=orm['account.User'], null=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now_add=True)),
        ))
        db.send_create_signal('report', ['ReportManga'])

        # Adding index on 'ReportManga', fields ['status', 'manga']
        db.create_index('report_manga', ['status', 'manga_id'])


    def backwards(self, orm):
        # Removing index on 'ReportManga', fields ['status', 'manga']
        db.delete_index('report_manga', ['status', 'manga_id'])

        # Deleting model 'ReportMangaResolution'
        db.delete_table('report_manga_resolution')

        # Deleting model 'ReportManga'
        db.delete_table('report_manga')


    models = {
        'account.user': {
            'Meta': {'object_name': 'User', 'db_table': "'user'"},
            'avatar': ('django.db.models.fields.files.FileField', [], {'blank': 'True', 'null': 'True', 'max_length': '255'}),
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
            'report_weight': ('django.db.models.fields.DecimalField', [], {'max_digits': '19', 'decimal_places': '10', 'default': '10'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'upload_limit': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'manga.manga': {
            'Meta': {'object_name': 'Manga', 'db_table': "'manga'"},
            'category': ('django.db.models.fields.CharField', [], {'default': "'OTHER'", 'db_index': 'True', 'max_length': '20'}),
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'to': "orm['tag.Tag']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'collection_part': ('django.db.models.fields.CharField', [], {'blank': 'True', 'null': 'True', 'max_length': '20'}),
            'cover': ('django.db.models.fields.files.FileField', [], {'null': 'True', 'max_length': '255'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'to': "orm['account.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'favorite_users': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'manga_favorites'", 'symmetrical': 'False', 'to': "orm['account.User']"}),
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'db_index': 'True', 'max_length': '20'}),
            'markdown': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'published_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'DRAFT'", 'db_index': 'True', 'max_length': '20'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'to': "orm['tag.Tag']", 'symmetrical': 'False'}),
            'tank': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'to': "orm['tag.Tag']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'tank_chapter': ('django.db.models.fields.CharField', [], {'blank': 'True', 'null': 'True', 'max_length': '20'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "'Untitled'", 'db_index': 'True', 'max_length': '100'}),
            'uncensored': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'to': "orm['account.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True', 'db_index': 'True'})
        },
        'report.reportmanga': {
            'Meta': {'object_name': 'ReportManga', 'index_together': "[('status', 'manga')]", 'db_table': "'report_manga'"},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True', 'null': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'to': "orm['account.User']", 'null': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'blank': 'True', 'null': 'True', 'max_length': '200'}),
            'manga': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['manga.Manga']"}),
            'quality': ('django.db.models.fields.CharField', [], {'default': "'UNKNOWN'", 'max_length': '20'}),
            'resolution': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'to': "orm['report.ReportMangaResolution']", 'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'OPEN'", 'max_length': '20'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'weight': ('django.db.models.fields.DecimalField', [], {'max_digits': '19', 'decimal_places': '10'})
        },
        'report.reportmangaresolution': {
            'Meta': {'object_name': 'ReportMangaResolution', 'db_table': "'report_manga_resolution'"},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True', 'null': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manga': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['manga.Manga']"}),
            'removed': ('django.db.models.fields.BooleanField', [], {})
        },
        'tag.tag': {
            'Meta': {'object_name': 'Tag', 'unique_together': "[('tag_type', 'name')]", 'db_table': "'tag'"},
            'cover': ('django.db.models.fields.files.FileField', [], {'blank': 'True', 'null': 'True', 'max_length': '255'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'to': "orm['account.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'tag_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'to': "orm['account.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True', 'db_index': 'True'})
        }
    }

    complete_apps = ['report']
