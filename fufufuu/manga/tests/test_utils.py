import zipfile
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from fufufuu.core.tests import BaseTestCase
from fufufuu.manga.models import MangaPage
from fufufuu.manga.utils import process_images, process_zipfile, MANGA_PAGE_LIMIT, MAX_IMAGE_FILE_SIZE


class MangaUtilTests(BaseTestCase):

    def test_process_image_empty(self):
        self.assertEqual([], process_images(self.manga, [], self.user))

    def test_process_images_page_limit(self):
        mp_list = []
        for i in range(1, MANGA_PAGE_LIMIT+1):
            mp_list.append(MangaPage(
                manga=self.manga,
                page=i,
                name='{}.jpg'.format(i),
                double=False,
            ))
        MangaPage.objects.bulk_create(mp_list)

        file = SimpleUploadedFile('test.jpg', b'content of image')
        errors = process_images(self.manga, [file], self.user)
        self.assertEqual(errors, ['There are currently 100 images; All other uploaded image files were ignored.'])

    def test_process_images_max_file_size(self):
        file_content = '0' * (MAX_IMAGE_FILE_SIZE+1)
        file = SimpleUploadedFile('test.jpg', bytes(file_content, 'utf-8'))
        errors = process_images(self.manga, [file], self.user)
        self.assertEqual(errors, ['test.jpg is over 10MB in size.'])

    def test_process_images_invalid_image(self):
        file_content = '0'
        file = SimpleUploadedFile('test.jpg', bytes(file_content, 'utf-8'))
        errors = process_images(self.manga, [file], self.user)
        self.assertEqual(errors, ['test.jpg failed to verify as an image file.'])

    def test_process_images_max_dimensions(self):
        image_file = self.create_test_image_file(width=8001, height=1200, format='JPEG')
        file = SimpleUploadedFile('test.jpg', image_file.getvalue())
        errors = process_images(self.manga, [file], self.user)
        self.assertEqual(errors, ['test.jpg is larger than 8000x8000 pixels.'])

    def test_process_images_unsupported_format(self):
        image_file = self.create_test_image_file(format='GIF')
        file = SimpleUploadedFile('test.gif', image_file.getvalue())
        errors = process_images(self.manga, [file], self.user)
        self.assertEqual(errors, ['test.gif is not a supported image type.'])

    def test_process_images(self):
        initial_page_count = MangaPage.objects.filter(manga=self.manga).count()

        content = self.create_test_image_file().getvalue()
        file1 = SimpleUploadedFile('test1.png', content)
        file2 = SimpleUploadedFile('test2.png', content)
        errors = process_images(self.manga, [file1, file2], self.user)
        self.assertEqual([], errors)

        actual_page_count = MangaPage.objects.filter(manga=self.manga).count()
        self.assertEqual(initial_page_count+2, actual_page_count)

    def test_process_zipfile_invalid(self):
        errors = process_zipfile(self.manga, BytesIO(), self.user)
        self.assertEqual(errors, ['The uploaded file is not a valid zip file.'])

    def test_process_zipfile_page_limit(self):
        upload_file = BytesIO()
        upload_file_zip = zipfile.ZipFile(upload_file, 'w')
        for i in range(MANGA_PAGE_LIMIT+1):
            upload_file_zip.writestr('{0:03d}.png'.format(i), bytes('0', 'utf-8'))
        upload_file_zip.close()

        errors = process_zipfile(self.manga, SimpleUploadedFile('test.zip', upload_file.getvalue()), self.user)
        self.assertEqual(errors[0], 'The zip archive contains more than 100 images, some images were ignored.')

    def test_process_zipfile(self):
        initial_page_count = MangaPage.objects.filter(manga=self.manga).count()
        content = self.create_test_image_file().getvalue()

        upload_file = BytesIO()
        upload_file_zip = zipfile.ZipFile(upload_file, 'w')
        upload_file_zip.writestr('01.png', bytes(content))
        upload_file_zip.writestr('02.png', bytes(content))
        upload_file_zip.writestr('03.png', bytes('0', 'utf-8'))
        upload_file_zip.close()

        errors = process_zipfile(self.manga, SimpleUploadedFile('test.zip', upload_file.getvalue()), self.user)
        self.assertEqual(errors, ['03.png failed to verify as an image file.'])

        actual_page_count = MangaPage.objects.filter(manga=self.manga).count()
        self.assertEqual(initial_page_count+2, actual_page_count)
