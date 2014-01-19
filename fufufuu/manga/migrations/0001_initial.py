# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
        ('account', '0001_initial'),
        ('tag', '0001_initial'),
    )

    def forwards(self, orm):
        # Adding model 'Manga'
        db.create_table('manga', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(db_index=True, auto_now=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, null=True, on_delete=models.SET_NULL, to=orm['account.User'], related_name='+')),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, null=True, on_delete=models.SET_NULL, to=orm['account.User'], related_name='+')),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, default='Untitled')),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=100)),
            ('markdown', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('html', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('cover', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=20, default='DRAFT', db_index=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=20, default='OTHER', db_index=True)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=20, default='en')),
            ('uncensored', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('tank', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, null=True, to=orm['tag.Tag'], related_name='+')),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, null=True, to=orm['tag.Tag'], related_name='+')),
            ('tank_chapter', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('collection_part', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('published_on', self.gf('django.db.models.fields.DateTimeField')(null=True, db_index=True)),
        ))
        db.send_create_signal('manga', ['Manga'])

        # Adding M2M table for field tags on 'Manga'
        m2m_table_name = db.shorten_name('manga_tags')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('manga', models.ForeignKey(orm['manga.manga'], null=False)),
            ('tag', models.ForeignKey(orm['tag.tag'], null=False))
        ))
        db.create_unique(m2m_table_name, ['manga_id', 'tag_id'])

        # Adding M2M table for field favorite_users on 'Manga'
        m2m_table_name = db.shorten_name('manga_favorite_users')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('manga', models.ForeignKey(orm['manga.manga'], null=False)),
            ('user', models.ForeignKey(orm['account.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['manga_id', 'user_id'])

        # Adding model 'MangaHistory'
        db.create_table('manga_history', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('manga', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['manga.Manga'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, default='Untitled')),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=100)),
            ('markdown', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('html', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('cover', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=20, default='VANILLA', db_index=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=20, default='DRAFT', db_index=True)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=20, default='en')),
            ('uncensored', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('tank', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, null=True, to=orm['tag.Tag'], related_name='+')),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, null=True, to=orm['tag.Tag'], related_name='+')),
            ('tank_chapter', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('collection_part', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('manga', ['MangaHistory'])

        # Adding M2M table for field tags on 'MangaHistory'
        m2m_table_name = db.shorten_name('manga_history_tags')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mangahistory', models.ForeignKey(orm['manga.mangahistory'], null=False)),
            ('tag', models.ForeignKey(orm['tag.tag'], null=False))
        ))
        db.create_unique(m2m_table_name, ['mangahistory_id', 'tag_id'])

        # Adding model 'MangaPage'
        db.create_table('manga_page', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('manga', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['manga.Manga'])),
            ('double', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('page', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('image', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
        ))
        db.send_create_signal('manga', ['MangaPage'])

        # Adding model 'MangaArchive'
        db.create_table('manga_archive', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('manga', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['manga.Manga'], unique=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('downloads', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('manga', ['MangaArchive'])


    def backwards(self, orm):
        # Deleting model 'Manga'
        db.delete_table('manga')

        # Removing M2M table for field tags on 'Manga'
        db.delete_table(db.shorten_name('manga_tags'))

        # Removing M2M table for field favorite_users on 'Manga'
        db.delete_table(db.shorten_name('manga_favorite_users'))

        # Deleting model 'MangaHistory'
        db.delete_table('manga_history')

        # Removing M2M table for field tags on 'MangaHistory'
        db.delete_table(db.shorten_name('manga_history_tags'))

        # Deleting model 'MangaPage'
        db.delete_table('manga_page')

        # Deleting model 'MangaArchive'
        db.delete_table('manga_archive')


    models = {
        'account.user': {
            'Meta': {'db_table': "'user'", 'object_name': 'User'},
            'avatar': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'comment_limit': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '254', 'blank': 'True'}),
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'markdown': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'upload_limit': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'})
        },
        'manga.manga': {
            'Meta': {'db_table': "'manga'", 'object_name': 'Manga'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '20', 'default': "'OTHER'", 'db_index': 'True'}),
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'null': 'True', 'to': "orm['tag.Tag']", 'related_name': "'+'"}),
            'collection_part': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'cover': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['account.User']", 'related_name': "'+'"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'favorite_users': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'symmetrical': 'False', 'to': "orm['account.User']", 'related_name': "'manga_favorites'"}),
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '20', 'default': "'en'"}),
            'markdown': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'published_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20', 'default': "'DRAFT'", 'db_index': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'to': "orm['tag.Tag']", 'symmetrical': 'False'}),
            'tank': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'null': 'True', 'to': "orm['tag.Tag']", 'related_name': "'+'"}),
            'tank_chapter': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'default': "'Untitled'"}),
            'uncensored': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['account.User']", 'related_name': "'+'"}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'auto_now': 'True', 'blank': 'True'})
        },
        'manga.mangaarchive': {
            'Meta': {'db_table': "'manga_archive'", 'object_name': 'MangaArchive'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'downloads': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manga': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['manga.Manga']", 'unique': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'manga.mangafavorite': {
            'Meta': {'db_table': "'manga_favorite_users'", 'object_name': 'MangaFavorite', 'managed': 'False'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manga': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['manga.Manga']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.User']"})
        },
        'manga.mangahistory': {
            'Meta': {'db_table': "'manga_history'", 'object_name': 'MangaHistory'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '20', 'default': "'VANILLA'", 'db_index': 'True'}),
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'null': 'True', 'to': "orm['tag.Tag']", 'related_name': "'+'"}),
            'collection_part': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'cover': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {}),
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '20', 'default': "'en'"}),
            'manga': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['manga.Manga']"}),
            'markdown': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20', 'default': "'DRAFT'", 'db_index': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'to': "orm['tag.Tag']", 'symmetrical': 'False'}),
            'tank': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'null': 'True', 'to': "orm['tag.Tag']", 'related_name': "'+'"}),
            'tank_chapter': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'default': "'Untitled'"}),
            'uncensored': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'manga.mangahistorytag': {
            'Meta': {'db_table': "'manga_history_tags'", 'object_name': 'MangaHistoryTag', 'managed': 'False'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mangahistory': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['manga.MangaHistory']"}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.Tag']"})
        },
        'manga.mangapage': {
            'Meta': {'ordering': "('page',)", 'db_table': "'manga_page'", 'object_name': 'MangaPage'},
            'double': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'manga': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['manga.Manga']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'page': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'manga.mangatag': {
            'Meta': {'db_table': "'manga_tags'", 'object_name': 'MangaTag', 'managed': 'False'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manga': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['manga.Manga']"}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.Tag']"})
        },
        'tag.tag': {
            'Meta': {'db_table': "'tag'", 'object_name': 'Tag', 'unique_together': "[('tag_type', 'name')]"},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['account.User']", 'related_name': "'+'"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'tag_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['account.User']", 'related_name': "'+'"}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['manga']
