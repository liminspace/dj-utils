# coding=utf-8
from __future__ import absolute_import
import StringIO
from PIL import Image
import imghdr
from dj_utils.upload import truncate_uploaded_file


def image_get_format(f):
    """
    Визначає формат зображення з файлу f.
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
    """
    f.seek(0)
    return imghdr.what(f)


def is_image(f, types=('png', 'jpeg', 'gif')):
    """
    Перевіряє, чи файл зображення і встановлює йому вірний тип.
    """
    t = image_get_format(f)
    if t in types:
        f.content_type = 'image/%s' % t
        return True
    return False


def image_sizelimit(f, max_size=(800, 800), quality=90):
    """
    Зменшує зображення, якщо воно надто велике
    """
    f.seek(0)
    img = Image.open(f)
    cf = img.format
    x, y = max_size
    if img.size[0] > x or img.size[1] > y:
        if img.size[0] > x:
            y = max(x * img.size[1] / img.size[0], 1)
        if img.size[1] > y:
            x = max(y * img.size[0] / img.size[1], 1)
        t = img.resize((x, y), Image.ANTIALIAS)
        del img
        truncate_uploaded_file(f)
        if cf == 'JPEG':
            t.save(f.file, cf, quality=quality)
        else:
            t.save(f.file, cf)
        del t
        f.file.seek(0, 2)
        f.size = f.file.tell()
    return cf.lower()


def image_convert_to_jpeg(f, quality=90):
    f.seek(0)
    img = Image.open(f)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img.load()  # need read file!
    truncate_uploaded_file(f)
    img.save(f.file, 'JPEG', quality=quality)
    del img
    f.file.seek(0, 2)
    f.size = f.file.tell()


# def image_get_size(f):
#     """
#     Визначає розмір зображення з файлу f.
#     Повертає:
#         (width, height)
#     """
#     f.seek(0)
#     img = Image.open(f)
#     return img.size


# def image_convert(f, img_format='jpeg', quality=90):
#     """
#     Конвертує файл зображення f в format.
#     """
#     assert img_format in ('jpeg', 'png', 'gif')
#     f.seek(0)
#     img = Image.open(f)
#     if img.mode != 'RGB':
#         img = img.convert('RGB')
#     img.load()  # need read file!
#     truncate_uploaded_file(f)
#     if img_format == 'jpeg':
#         img.save(f.file, img_format, quality=quality)
#     else:
#         img.save(f.file, img_format)
#     f.file.seek(0, 2)
#     f.size = f.file.tell()
#     f.content_type = 'image/%s' % img_format


def get_thumbnail(f, size=(160, 160), img_format='jpeg', quality=90):
    assert isinstance(size, (list, tuple)) and len(size) == 2
    assert img_format in ('jpeg', 'png', 'gif')
    assert 0 < quality <= 100
    f.seek(0)
    img = Image.open(f)
    img.thumbnail(size, Image.ANTIALIAS)
    t = StringIO.StringIO()
    if img_format == 'jpeg':
        img.save(t, format=img_format, quality=quality)
    else:
        img.save(t, format=img_format)
    return t
