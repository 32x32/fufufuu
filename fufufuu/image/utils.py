from io import BytesIO
from PIL import Image, ImageFile, ImageOps
from fufufuu.image.transforms import specs


class ImageTransformer(object):

    @classmethod
    def transform(cls, key_type, source):
        """
        return a BytesIO object with the transformed image
        """

        file = open(source, 'rb')
        im = Image.open(file)
        ImageFile.MAXBLOCK = im.size[0] * im.size[1]

        try:
            im.load()
        except IOError:
            # we can "safely" ignore the exception that occurs at this point
            # http://stackoverflow.com/questions/12984426/python-pil-ioerror-image-file-truncated-with-big-images
            pass

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
            im.thumbnail((spec['width'], spec['height']), Image.ANTIALIAS)

        output = BytesIO()
        im.save(output, format='JPEG', quality=spec.get('quality', 75), optimize=True, progressive=False)

        file.close()

        return output
