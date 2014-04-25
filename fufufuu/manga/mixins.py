from collections import defaultdict
from fufufuu.core.languages import Language
from fufufuu.core.templates import TEMPLATE_ENV
from fufufuu.image.enums import ImageKeyType
from fufufuu.image.filters import image_resize
from fufufuu.manga.enums import MangaStatus, MangaCategory
from fufufuu.tag.enums import TagType


class MangaMixin:

    @property
    def status_display(self): return MangaStatus.choices_dict[self.status]

    @property
    def category_display(self): return MangaCategory.choices_dict[self.category]

    @property
    def language_display(self): return Language.choices_dict[self.language]

    @property
    def tag_dictionary(self):
        if hasattr(self, '_tag_dictionary'):
            return self._tag_dictionary

        self.update_tag_dictionary()
        return self._tag_dictionary

    @property
    def archive_name(self):
        tag_dict = self.tag_dictionary
        authors = ', '.join([t.name for t in tag_dict[TagType.AUTHOR]])
        circles = ', '.join([t.name for t in tag_dict[TagType.CIRCLE]])
        scanlators  = ', '.join([t.name for t in tag_dict[TagType.SCANLATOR]])

        filename = []
        if scanlators:
            filename.append('[{}]'.format(scanlators))
        if circles and authors:
            filename.append('[{} ({})]'.format(circles, authors))
        elif circles:
            filename.append('[{}]'.format(circles))
        elif authors:
            filename.append('({})'.format(authors))

        filename.append('{}'.format(self.title))

        name = ' '.join(filename)[:196] + '.zip'
        name = name.replace('] [', '][').replace('] (', '](')
        return name

    @property
    def cover_url(self):
        return image_resize(self.cover, ImageKeyType.MANGA_COVER, self.id)

    @property
    def info_text(self):
        return TEMPLATE_ENV.get_template('manga/manga-archive-info.txt').render({'manga': self})

    def update_tag_dictionary(self):
        self._tag_dictionary = defaultdict(list)
        for tag in self.tags.all():
            self._tag_dictionary[tag.tag_type].append(tag)
