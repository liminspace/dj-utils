# coding=utf-8
from __future__ import absolute_import
from PIL import Image
from PIL.ImageDraw import ImageDraw
from StringIO import StringIO
from django.core.files.uploadedfile import UploadedFile
from django.test import TestCase
from dj_utils.image import adjust_image, image_get_format, is_image


def create_test_image(w, h):
    img = Image.new('RGB', (w, h), color='#FFFFFF')
    d = ImageDraw(img)
    d.line((-1, -1) + img.size, fill='#888888', width=2)
    d.line((-1, img.size[1], img.size[0], -1), fill='#888888', width=2)
    return img


def get_img_file(img, img_format='JPEG', jpeg_quality=100):
    f = StringIO()
    img.save(f, img_format, quality=jpeg_quality)
    return f


class TestAdjustImage(TestCase):
    def setUp(self):
        self.img_200x200 = create_test_image(200, 200)
        self.img_300x300 = create_test_image(300, 300)
        self.img_400x200 = create_test_image(400, 200)
        self.img_200x400 = create_test_image(200, 400)

    def make_files_for_images(self):
        self.f_200x200_jpeg = get_img_file(self.img_200x200)
        self.f_300x300_jpeg = get_img_file(self.img_300x300)
        self.f_400x200_jpeg = get_img_file(self.img_400x200)
        self.f_200x400_jpeg = get_img_file(self.img_200x400)
        self.f_200x200_png = get_img_file(self.img_200x200, img_format='PNG')
        self.f_300x300_png = get_img_file(self.img_300x300, img_format='PNG')
        self.f_400x200_png = get_img_file(self.img_400x200, img_format='PNG')
        self.f_200x400_png = get_img_file(self.img_200x400, img_format='PNG')

    def assertImageSizeIs(self, f_img, size, msg=None):
        f_img.seek(0)
        img = Image.open(f_img)
        if img.size != size:
            raise self.failureException(msg)

    def assertImageFormat(self, f_img, img_format, msg=None):
        f_img.seek(0)
        img = Image.open(f_img)
        if img.format.lower() != img_format.lower():
            raise self.failureException(msg)

    def test_size_not_fill_not_stretch(self):
        self.make_files_for_images()
        self.assertFalse(adjust_image(self.f_200x200_png, (200, 200)))
        self.assertFalse(adjust_image(self.f_300x300_png, (300, 400)))
        self.assertTrue(adjust_image(self.f_400x200_jpeg, (200, 200)))
        self.assertImageSizeIs(self.f_400x200_jpeg, (200, 100))
        self.assertTrue(adjust_image(self.f_200x400_jpeg, (200, 200)))
        self.assertImageSizeIs(self.f_200x400_jpeg, (100, 200))

    def test_size_not_fill_stretch(self):
        self.make_files_for_images()
        self.assertTrue(adjust_image(self.f_200x200_jpeg, (200, 200), stretch=True))
        self.assertFalse(adjust_image(self.f_300x300_jpeg, (300, 400), stretch=True, force_jpeg_save=False))
        self.assertTrue(adjust_image(self.f_400x200_jpeg, (500, 500), stretch=True))
        self.assertImageSizeIs(self.f_400x200_jpeg, (500, 250))

    def test_size_fill_not_stretch(self):
        self.make_files_for_images()
        self.assertFalse(adjust_image(self.f_200x200_png, (200, 200), fill=True))
        self.assertTrue(adjust_image(self.f_400x200_jpeg, (100, 100), fill=True))
        self.assertImageSizeIs(self.f_400x200_jpeg, (100, 100))
        self.assertTrue(adjust_image(self.f_200x400_jpeg, (400, 500), fill=True))
        self.assertImageSizeIs(self.f_200x400_jpeg, (200, 250))
        self.assertTrue(adjust_image(self.f_300x300_jpeg, (150, 100), fill=True))
        self.assertImageSizeIs(self.f_300x300_jpeg, (150, 100))

    def test_size_fill_stretch(self):
        self.make_files_for_images()
        self.assertFalse(adjust_image(self.f_200x200_png, (200, 200), fill=True, stretch=True))
        self.assertTrue(adjust_image(self.f_300x300_jpeg, (400, 350), fill=True, stretch=True))
        self.assertImageSizeIs(self.f_300x300_jpeg, (400, 350))

    def test_format(self):
        self.make_files_for_images()
        self.assertTrue(adjust_image(self.f_200x200_jpeg, (200, 200), new_format='PNG'))
        self.assertImageFormat(self.f_200x200_jpeg, 'PNG')

    def test_autosize(self):
        self.make_files_for_images()
        self.assertTrue(adjust_image(self.f_200x200_jpeg, (150, None), fill=True, stretch=True))
        self.assertImageSizeIs(self.f_200x200_jpeg, (150, 150))
        self.assertTrue(adjust_image(self.f_200x400_jpeg, (None, 300), fill=True, stretch=True))
        self.assertImageSizeIs(self.f_200x400_jpeg, (150, 300))

    def test_uploaded_file(self):
        self.make_files_for_images()
        uf = UploadedFile(file=self.f_200x200_jpeg, name='200x200.jpeg', content_type='image/jpeg',
                          size=len(self.f_200x200_jpeg.getvalue()))
        self.assertTrue(adjust_image(uf, (120, 120), new_format='PNG'))
        self.assertImageSizeIs(uf.file, (120, 120))
        self.assertEqual(uf.content_type, 'image/png')

    def test_new_image(self):
        self.make_files_for_images()
        self.assertIsInstance(adjust_image(self.f_200x200_jpeg, return_new_image=True), StringIO)


class TestImageGetFormat(TestCase):
    def setUp(self):
        self.img_jpeg = get_img_file(create_test_image(100, 100))
        self.img_png = get_img_file(create_test_image(100, 100), img_format='PNG')
        self.img_gif = get_img_file(create_test_image(100, 100), img_format='GIF')

    def test_format(self):
        self.assertEqual(image_get_format(self.img_jpeg), 'jpeg')
        self.assertEqual(image_get_format(self.img_png), 'png')
        self.assertEqual(image_get_format(self.img_gif), 'gif')

    def test_bad_format(self):
        self.assertIsNone(image_get_format(StringIO('x' * 1000)))


class TestIsImage(TestCase):
    def setUp(self):
        self.img_jpeg = get_img_file(create_test_image(100, 100))
        self.img_png = get_img_file(create_test_image(100, 100), img_format='PNG')
        self.img_gif = get_img_file(create_test_image(100, 100), img_format='GIF')

    def test_check(self):
        self.assertTrue(is_image(self.img_jpeg, ('JpEg', 'PnG', 'GIF')))
        self.assertFalse(is_image(self.img_jpeg, ('PnG', 'GIF')))
        uf = UploadedFile(file=self.img_jpeg, name='test.jpeg', content_type='empty',
                          size=len(self.img_jpeg.getvalue()))
        self.assertTrue(is_image(uf, ('jpeg',), set_content_type=False))
        self.assertEqual(uf.content_type, 'empty')
        is_image(uf, ('jpeg',))
        self.assertEqual(uf.content_type, 'image/jpeg')
