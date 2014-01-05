from io import BytesIO
from PIL import Image, ImageFile, ImageOps
from django.core.files.base import File, ContentFile

from fufufuu.image.transforms import specs


class ImageTransformer(object):

    @classmethod
    def transform(cls, key_type, source):
        """
        Return a ContentFile with the transformed image
        """

        im = Image.open(source)
        ImageFile.MAXBLOCK = im.size[0] * im.size[1]

        if im.mode != 'RGB':
            im = im.convert('RGB')

        spec = specs[key_type]
        if spec.get('crop'):
            w, h = im.size[0], im.size[1]
            if w <= spec['width'] or h <= spec['height']:
                target_ratio = spec['width'] / spec['height']
                source_ratio = w / h
                if source_ratio >= target_ratio:
                    w = h * target_ratio
                else:
                    h = w / target_ratio
                w, h = int(w), int(h)
                im = ImageOps.fit(im, (w, h), Image.ANTIALIAS)
            else:
                im = ImageOps.fit(im, (spec['width'], spec['height']), Image.ANTIALIAS)
        else:
            im.thumbnail(spec['width'], spec['height'], Image.ANTIALIAS)

        output = BytesIO()
        im.save(output, format='JPEG', quality=spec.get('quality', 75), optimize=True, progressive=False)
        return ContentFile(output.getvalue())
