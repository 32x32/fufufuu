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
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, on_delete=models.SET_NULL, to=orm['account.User'], blank=True)),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, on_delete=models.SET_NULL, to=orm['account.User'], blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default='Untitled', max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=100)),
            ('markdown', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('html', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('cover', self.gf('django.db.models.fields.files.FileField')(null=True, max_length=100)),
            ('status', self.gf('django.db.models.fields.CharField')(db_index=True, default='DRAFT', max_length=20)),
            ('category', self.gf('django.db.models.fields.CharField')(db_index=True, default='OTHER', max_length=20)),
            ('language', self.gf('django.db.models.fields.CharField')(default='en', max_length=20)),
            ('uncensored', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('tank', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['tag.Tag'], blank=True)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['tag.Tag'], blank=True)),
            ('tank_chapter', self.gf('django.db.models.fields.CharField')(null=True, blank=True, max_length=20)),
            ('collection_part', self.gf('django.db.models.fields.CharField')(null=True, blank=True, max_length=20)),
            ('published_on', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True)),
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
            ('title', self.gf('django.db.models.fields.CharField')(default='Untitled', max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=100)),
            ('markdown', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('html', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('cover', self.gf('django.db.models.fields.files.FileField')(null=True, max_length=100)),
            ('category', self.gf('django.db.models.fields.CharField')(db_index=True, default='VANILLA', max_length=20)),
            ('status', self.gf('django.db.models.fields.CharField')(db_index=True, default='DRAFT', max_length=20)),
            ('language', self.gf('django.db.models.fields.CharField')(default='en', max_length=20)),
            ('uncensored', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('tank', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['tag.Tag'], blank=True)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['tag.Tag'], blank=True)),
            ('tank_chapter', self.gf('django.db.models.fields.CharField')(null=True, blank=True, max_length=20)),
            ('collection_part', self.gf('django.db.models.fields.CharField')(null=True, blank=True, max_length=20)),
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
            ('name', self.gf('django.db.models.fields.CharField')(null=True, max_length=100)),
        ))
        db.send_create_signal('manga', ['MangaPage'])

        # Adding model 'MangaArchive'
        db.create_table('manga_archive', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('manga', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['manga.Manga'])),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('downloads', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
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
            'avatar': ('django.db.models.fields.files.FileField', [], {'null': 'True', 'blank': 'True', 'max_length': '100'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'blank': 'True', 'max_length': '254'}),
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'markdown': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'manga.manga': {
            'Meta': {'db_table': "'manga'", 'object_name': 'Manga'},
            'category': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'default': "'OTHER'", 'max_length': '20'}),
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['tag.Tag']", 'blank': 'True'}),
            'collection_part': ('django.db.models.fields.CharField', [], {'null': 'True', 'blank': 'True', 'max_length': '20'}),
            'cover': ('django.db.models.fields.files.FileField', [], {'null': 'True', 'max_length': '100'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['account.User']", 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'favorite_users': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'manga_favorites'", 'to': "orm['account.User']", 'symmetrical': 'False'}),
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '20'}),
            'markdown': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'published_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'default': "'DRAFT'", 'max_length': '20'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'to': "orm['tag.Tag']", 'symmetrical': 'False'}),
            'tank': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['tag.Tag']", 'blank': 'True'}),
            'tank_chapter': ('django.db.models.fields.CharField', [], {'null': 'True', 'blank': 'True', 'max_length': '20'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "'Untitled'", 'max_length': '100'}),
            'uncensored': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['account.User']", 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'})
        },
        'manga.mangaarchive': {
            'Meta': {'db_table': "'manga_archive'", 'object_name': 'MangaArchive'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'downloads': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manga': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['manga.Manga']"})
        },
        'manga.mangafavorite': {
            'Meta': {'managed': 'False', 'db_table': "'manga_favorite_users'", 'object_name': 'MangaFavorite'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manga': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['manga.Manga']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.User']"})
        },
        'manga.mangahistory': {
            'Meta': {'db_table': "'manga_history'", 'object_name': 'MangaHistory'},
            'category': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'default': "'VANILLA'", 'max_length': '20'}),
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['tag.Tag']", 'blank': 'True'}),
            'collection_part': ('django.db.models.fields.CharField', [], {'null': 'True', 'blank': 'True', 'max_length': '20'}),
            'cover': ('django.db.models.fields.files.FileField', [], {'null': 'True', 'max_length': '100'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {}),
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '20'}),
            'manga': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['manga.Manga']"}),
            'markdown': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'default': "'DRAFT'", 'max_length': '20'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'to': "orm['tag.Tag']", 'symmetrical': 'False'}),
            'tank': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['tag.Tag']", 'blank': 'True'}),
            'tank_chapter': ('django.db.models.fields.CharField', [], {'null': 'True', 'blank': 'True', 'max_length': '20'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "'Untitled'", 'max_length': '100'}),
            'uncensored': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'manga.mangahistorytag': {
            'Meta': {'managed': 'False', 'db_table': "'manga_history_tags'", 'object_name': 'MangaHistoryTag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manga_history': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['manga.MangaHistory']"}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.Tag']"})
        },
        'manga.mangapage': {
            'Meta': {'object_name': 'MangaPage', 'db_table': "'manga_page'", 'ordering': "('page',)"},
            'double': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'manga': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['manga.Manga']"}),
            'name': ('django.db.models.fields.CharField', [], {'null': 'True', 'max_length': '100'}),
            'page': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'manga.mangatag': {
            'Meta': {'managed': 'False', 'db_table': "'manga_tags'", 'object_name': 'MangaTag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manga': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['manga.Manga']"}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.Tag']"})
        },
        'tag.tag': {
            'Meta': {'db_table': "'tag'", 'object_name': 'Tag'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag_type': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20'})
        }
    }

    complete_apps = ['manga']
