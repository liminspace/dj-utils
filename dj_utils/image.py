# coding=utf-8
from __future__ import absolute_import
from StringIO import StringIO
import imghdr
from PIL import Image
from django.core.files.uploadedfile import UploadedFile
from dj_utils.file import truncate_file


def image_get_format(f):
    """
    Визначає формат зображення.
    Повертає:
        'rgb'  - SGI ImgLib Files
        'gif'  - GIF 87a and 89a Files
        'pbm'  - Portable Bitmap Files
        'pgm'  - Portable Graymap Files
        'ppm'  - Portable Pixmap Files
        'tiff' - TIFF Files
        'rast' - Sun Raster Files
        'xbm'  - X Bitmap Files
        'jpeg' - JPEG data in JFIF or Exif formats
        'bmp'  - BMP files
        'png'  - Portable Network Graphics
    Приклад:
        if image_get_format(request.FILES['image']) == 'jpeg':
            print 'Image is JPEG'

        if image_get_format(open('/tmp/image.png', 'rb')) == 'png':
            print 'File is PNG'
    """
    f.seek(0)
    t = imghdr.what(f)
    if isinstance(t, basestring):
        t = t.lower()
    return t


def is_image(f, types=('png', 'jpeg', 'gif'), set_content_type=True):
    """
    Повертає True, якщо файл є зображенням (типу types) і встановлює йому вірний content_type.
    Приклад:
        if is_image(request.FILES['file']):
            print 'File is image'

        if is_image(open('/tmp/image.jpeg', 'rb')):
            print 'File is image'
    """
    assert isinstance(types, (list, tuple))
    types = [t.lower() for t in types]
    t = image_get_format(f)
    if t not in types:
        return False
    if isinstance(f, UploadedFile) and set_content_type:
        f.content_type = 'image/%s' % t
    return True


def adjust_image(f, max_size=(800, 800), new_format=None, jpeg_quality=90, fill=False, stretch=False,
                 return_new_image=False):
    """
    Підганяє зображення під параметри.
    max_size - максимальний розмір картинки. один з розмірів може бути None (авто)
    new_format - формат файлу (jpeg, png, gif). якщо None, тоді буде використаний формат оригіналу
    jpeg_quality - якість JPEG
    fill - чи зображення має бути заповненим при обрізці (інакше буде вписане)
    stretch - чи розтягувати, якщо картинка замаленька
    return_new_image - якщо True, тоді буде повертатись новий об'єкт StringIO картинки. Інакше bool, чи файл змінювався.
    """
    assert isinstance(max_size, (list, tuple)) and len(max_size) == 2
    assert 0 < jpeg_quality <= 100
    if new_format:
        new_format = new_format.lower()
        assert new_format in ('jpeg', 'png', 'gif')
    f.seek(0)
    img = Image.open(f)
    max_width, max_height = max_size
    img_width, img_height = img.size
    img_format = img.format.lower()
    ch_size = ch_format = False
    if max_width is None:
        max_width = int(round((img_width / float(img_height)) * max_height))
    elif max_height is None:
        max_height = int(round((img_height / float(img_width)) * max_width))
    if (img_width, img_height) != (max_width, max_height):
        tasks = []
        if fill:
            if (img_width < max_width or img_height < max_height) and not stretch:
                k = max(max_width / float(img_width), max_height / float(img_height))
                w, h = int(round(max_width / k)), int(round(max_height / k))
                left, top = int(round((img_width - w) / 2.)), int(round((img_height - h) / 2.))
                tasks.append(('crop', ((left, top, left + w, top + h),), {}))
            else:
                k = min(img_width / float(max_width), img_height / float(max_height))
                w, h = int(round(img_width / k)), int(round(img_height / k))
                tasks.append(('resize', ((w, h), Image.LANCZOS), {}))
                left, top = int(round((w - max_width) / 2.)), int(round((h - max_height) / 2.))
                tasks.append(('crop', ((left, top, left + max_width, top + max_height),), {}))
        elif ((img_width > max_width or img_height > max_height) or
                (img_width < max_width and img_height < max_height and stretch)):
            k = max(img_width / float(max_width), img_height / float(max_height))
            w, h = int(round(img_width / k)), int(round(img_height / k))
            tasks.append(('resize', ((w, h), Image.LANCZOS), {}))
        for img_method, method_args, method_kwargs in tasks:
            if ((img_method == 'resize' and method_args[0] == (img_width, img_height)) or
                    (img_method == 'crop' and method_args[0] == (0, 0, img.size[0], img.size[1]))):
                continue
            img = getattr(img, img_method)(*method_args, **method_kwargs)
            ch_size = True
    if new_format and new_format != img_format:
        ch_format = True
        img_format = new_format
    if return_new_image:
        f = StringIO()
        img.save(f, img_format, jpeg_quality=jpeg_quality)
        return f
    if ch_size or ch_format:
        img.load()
        truncate_file(f)
        img.save(f, img_format, jpeg_quality=jpeg_quality)
        if isinstance(f, UploadedFile):
            f.seek(0, 2)
            f.size = f.tell()
            f.content_type = 'image/%s' % new_format
    return ch_size or ch_format


def get_thumbnail(f, size=(200, 200), new_format=None, jpeg_quality=85, fill=True, stretch=True):
    return adjust_image(f, max_size=size, new_format=new_format, jpeg_quality=jpeg_quality, fill=fill, stretch=stretch,
                        return_new_image=True)


def get_thumbnail_old(f, size=(200, 200), new_format='jpeg', jpeg_quality=85):
    """
    Створює мініатюру зображення з розміром size та типом img_format.
    Для jpeg використовується якість quality.
    Повертається файл зображення у вигляді об'єкту StringIO.
    Приклад:
        thumb = get_thumbnail(request.FILES['image'], size=(120, 120), quality=80)
        open('/tmp/thumb.jpeg', 'wb').write(thumb.getvalue())

        thumb = get_thumbnail(open('/tmp/thumb.jpeg', 'rb'), size=(120, 120), quality=80)
        open('/tmp/thumb.jpeg', 'wb').write(thumb.getvalue())
    """
    assert isinstance(size, (list, tuple)) and len(size) == 2
    assert new_format in ('jpeg', 'png', 'gif')
    assert 0 < jpeg_quality <= 100
    f.seek(0)
    img = Image.open(f)
    img.thumbnail(size, Image.BICUBIC)
    t = StringIO()
    img.save(t, format=new_format, quality=jpeg_quality)
    return t
