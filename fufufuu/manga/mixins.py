from collections import defaultdict
from fufufuu.core.languages import Language
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

        self._tag_dictionary = defaultdict(list)
        for tag in self.tags.all():
            self._tag_dictionary[tag.tag_type].append(tag)
        return self._tag_dictionary

    @property
    def archive_name(self):
        tag_dict = self.tag_dictionary
        scanlators  = ', '.join([t.name for t in tag_dict[TagType.SCANLATOR]])

        filename = ['[{}]'.format(str(self.id))]
        if scanlators:
            filename.append('[{}]'.format(scanlators))
        filename.append(' {}'.format(self.title))

        return ''.join(filename)[:196] + '.zip'

    @property
    def cover_url(self):
        return image_resize(self.cover, ImageKeyType.MANGA_COVER, self.id)
