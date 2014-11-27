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
    return imghdr.what(f).lower()


def is_image(f, types=('png', 'jpeg', 'gif')):
    """
    Повертає True, якщо файл є зображенням (типу types) і встановлює йому вірний тип.
    Приклад:
        if is_image(request.FILES['file']):
            print 'File is image'

        if is_image(open('/tmp/image.jpeg', 'rb')):
            print 'File is image'
    """
    assert isinstance(types, (list, tuple))
    t = image_get_format(f)
    if t not in types:
        return False
    if isinstance(f, UploadedFile):
        f.content_type = 'image/%s' % t
    return True


def image_sizelimit(f, max_size=(800, 800), quality=90):
    """
    Зменшує зображення, якщо воно більше, ніж max_size.
    Тип файлу не змінюється.
    Якщо файл JPEG, тоді буде збереження в якості quality.
    Повертає True, якщо файл змінився.
    Приклад:
        image_sizelimit(request.FILES['img_1000x500'], max_size=(600, 600))  # на виході буде 600 x 300
        image_sizelimit(request.FILES['img_500x1000'], max_size=(600, 600))  # на виході буде 300 x 600
        image_sizelimit(request.FILES['img_300x400'], max_size=(600, 600))  # на виході буде 300 x 400

        with open('/tmp/img_800x900.png', 'rb+') as f:
            image_sizelimit(f, max_size=(600, 600))  # на виході буде 533 x 600
    """
    assert isinstance(max_size, (list, tuple)) and len(max_size) == 2
    assert 0 < quality <= 100
    f.seek(0)
    img = Image.open(f)
    max_width, max_height = max_size
    img_width, img_height = img.size
    if img_width < max_width and img_height < max_height:
        return False
    k = min(img_width / float(max_width), img_height / float(max_height))
    new_img = img.resize((int(round(img_width / k)), int(round(img_height / k))), Image.ANTIALIAS)
    img_format = img.format.lower()
    del img
    truncate_file(f)
    if img_format == 'jpeg':
        new_img.save(f, img_format, quality=quality)
    else:
        new_img.save(f, img_format)
    del new_img
    if isinstance(f, UploadedFile):
        f.seek(0, 2)
        f.size = f.tell()
    return True


def image_convert_type(f, new_format='jpeg', quality=90, force=False):
    """
    Конвертує зображення в new_format (jpeg, png, gif) і встановлює йому вірний тип.
    Для jpeg використовується якість quality.
    Якщо force=True, тоді файл буде перезберігатись навіть тоді, коли він вже є необхідного типу.
    Повертає True, якщо файл змінився.
    Приклад:
        image_convert_type(request.FILES['image'], new_format='jpeg', quality=95)

        with open('/tmp/img.png', 'rb+') as f:
            image_convert_type(f, new_format='jpeg', quality=95)
    """
    assert new_format in ('jpeg', 'png', 'gif')
    assert 0 < quality <= 100
    current_format = image_get_format(f)
    if new_format == current_format and not force:
        return False
    f.seek(0)
    img = Image.open(f)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img.load()  # need read file!
    truncate_file(f)
    if new_format == 'jpeg':
        img.save(f, new_format, quality=quality)
    else:
        img.save(f, new_format)
    del img
    if isinstance(f, UploadedFile):
        f.seek(0, 2)
        f.size = f.tell()
        f.content_type = 'image/%s' % new_format
    return True


def get_thumbnail(f, size=(160, 160), img_format='jpeg', quality=90):
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
    assert img_format in ('jpeg', 'png', 'gif')
    assert 0 < quality <= 100
    f.seek(0)
    img = Image.open(f)
    img.thumbnail(size, Image.ANTIALIAS)
    t = StringIO()
    if img_format == 'jpeg':
        img.save(t, format=img_format, quality=quality)
    else:
        img.save(t, format=img_format)
    return t
