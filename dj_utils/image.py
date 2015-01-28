# coding=utf-8
from __future__ import absolute_import
import os
import subprocess
from StringIO import StringIO
from contextlib import contextmanager
from PIL import Image, ImageFile
from django.core.files.uploadedfile import UploadedFile
from dj_utils.file import truncate_file
from dj_utils import settings as u_settings


def image_get_format(f):
    """
    Визначає формат зображення.
    Повертає:
        jpeg, png, gif і т.д.
        http://pillow.readthedocs.org/en/latest/handbook/image-file-formats.html
    Приклад:
        if image_get_format(request.FILES['image']) == 'jpeg':
            print 'Image is JPEG'

        if image_get_format(open('/tmp/image.png', 'rb')) == 'png':
            print 'File is PNG'
    """
    f.seek(0)
    try:
        img = Image.open(f)
        t = img.format.lower()
    except IOError:
        t = None
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
        f.name = os.path.splitext(f.name)[0] + '.' + t
    return True


@contextmanager
def image_save_buffer_fix(baxblock=1048576):
    before = ImageFile.MAXBLOCK
    ImageFile.MAXBLOCK = baxblock
    try:
        yield
    finally:
        ImageFile.MAXBLOCK = before


def _save_img(img, f, *args, **kwargs):
    modes = ({},
             {'mb_x': 5},
             {'mb_x': 10},
             {'mb_x': 10, 'disable_optimize': True},
             {'mb_x': 10, 'disable_optimize': True, 'disable_progressive': True})
    maxblock = img.size[0] * img.size[1]
    last_error = None
    for mode in modes:
        try:
            kw = kwargs.copy()
            if mode.get('disable_optimize'):
                kw.pop('optimize')
            if mode.get('disable_progressive'):
                kw.pop('progressive')
            with image_save_buffer_fix(maxblock * mode.get('mb_x', 1)):
                img.save(f, *args, **kw)
                last_error = None
                break
        except IOError, e:
            last_error = e
    if last_error:
        raise last_error
    if img.format == 'JPEG' and u_settings.DJU_IMG_USE_JPEGTRAN:
        f.seek(0)
        try:
            p = subprocess.Popen(['jpegtran', '-copy', 'none', '-optimize', '-progressive'],
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            r = p.communicate(f.read())[0]
        except IOError:
            r = None
        if r:
            truncate_file(f)
            f.write(r)


def get_image_as_rgb(f):
    f.seek(0)
    try:
        p = subprocess.Popen(['convert', '-colorspace', 'rgb', '-', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        r = p.communicate(f.read())[0]
    except IOError:
        r = None
    if r:
        return Image.open(StringIO(r))


def optimize_png_file(f, o=None):
    """
    Використовує утиліту pngquant для оптимізації картинки.
    f - шлях до файлу або file-об'єкт
    o - шлях до вихідного фафлу або file-об'єкт для збереження результату
    * f і o не можуть бути різного типу
    """
    if isinstance(f, basestring):
        if o is None:
            o = f
        else:
            assert isinstance(o, basestring)
        try:
            subprocess.check_call(['pngquant', '--force', '--output', o, f])
        except subprocess.CalledProcessError:
            return False
        return True
    assert hasattr(f, 'read')
    if o is None:
        o = f
    else:
        assert hasattr(o, 'write')
    f.seek(0)
    try:
        p = subprocess.Popen(['pngquant', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        r = p.communicate(f.read())[0]
    except IOError:
        r = None
    if r:
        truncate_file(o)
        o.write(r)
        return True
    return False


def adjust_image(f, max_size=(800, 800), new_format=None, jpeg_quality=90, fill=False, stretch=False,
                 return_new_image=False, force_jpeg_save=True):
    """
    Підганяє зображення під параметри.
    max_size - максимальний розмір картинки. один з розмірів може бути None (авто)
    new_format - формат файлу (jpeg, png, gif). якщо None, тоді буде використаний формат оригіналу
    jpeg_quality - якість JPEG
    fill - чи зображення має бути заповненим при обрізці (інакше буде вписане)
    stretch - чи розтягувати, якщо картинка замаленька
    return_new_image - якщо True, тоді буде повертатись новий об'єкт StringIO картинки. Інакше bool, чи файл змінювався.
    force_jpeg_save - якщо True, тоді якщо файл JPEG, то він буде перезбережений в будь-якому випадку
    """
    assert isinstance(max_size, (list, tuple)) and len(max_size) == 2
    assert 0 < jpeg_quality <= 100
    if new_format:
        new_format = new_format.lower()
        assert new_format in ('jpeg', 'png', 'gif')
    f.seek(0)
    img = Image.open(f)
    if img.format == 'JPEG' and img.mode == 'CMYK' and u_settings.DJU_IMG_CONVERT_JPEG_TO_RGB:
        img = get_image_as_rgb(f) or img
    max_width, max_height = max_size
    img_width, img_height = img.size
    img_format = img.format.lower()
    ch_size = ch_format = False
    if max_width is None:
        max_width = int(((img_width / float(img_height)) * max_height))
    elif max_height is None:
        max_height = int(((img_height / float(img_width)) * max_width))
    if (img_width, img_height) != (max_width, max_height):
        tasks = []
        if fill:
            if (img_width < max_width or img_height < max_height) and not stretch:
                k = max(max_width / float(img_width), max_height / float(img_height))
                w, h = max_width / k, max_height / k
                left, top = int((img_width - w) / 2.), int((img_height - h) / 2.)
                tasks.append(('crop', ((left, top, int(left + w), int(top + h)),), {}))
            else:
                k = min(img_width / float(max_width), img_height / float(max_height))
                w, h = img_width / k, img_height / k
                tasks.append(('resize', ((int(w), int(h)), Image.LANCZOS), {}))
                left, top = int((w - max_width) / 2.), int((h - max_height) / 2.)
                tasks.append(('crop', ((left, top, left + max_width, top + max_height),), {}))
        elif ((img_width > max_width or img_height > max_height) or
                (img_width < max_width and img_height < max_height and stretch)):
            k = max(img_width / float(max_width), img_height / float(max_height))
            w, h = int(img_width / k), int(img_height / k)
            tasks.append(('resize', ((w, h), Image.LANCZOS), {}))
        for img_method, method_args, method_kwargs in tasks:
            if ((img_method == 'resize' and method_args[0] == (img_width, img_height)) or
                    (img_method == 'crop' and method_args[0] == (0, 0, img.size[0], img.size[1]))):
                continue
            img = getattr(img, img_method)(*method_args, **method_kwargs)
            ch_size = True
    if new_format and new_format != img_format:
        img_format = new_format
        ch_format = True
    if not ch_format and img_format == 'jpeg' and force_jpeg_save:
        ch_format = True
    if return_new_image:
        t = StringIO()
        _save_img(img, t, format=img_format, quality=jpeg_quality, progressive=True, optimize=True)
        return t
    if ch_size or ch_format:
        img.load()
        truncate_file(f)
        _save_img(img, f, format=img_format, quality=jpeg_quality, progressive=True, optimize=True)
        if isinstance(f, UploadedFile):
            f.seek(0, 2)
            f.size = f.tell()
            f.content_type = 'image/%s' % new_format
            f.name = os.path.splitext(f.name)[0] + '.' + img_format
    return ch_size or ch_format
