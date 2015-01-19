# coding=utf-8
from __future__ import absolute_import
import copy
import glob
import os
import re
import datetime
from django.conf import settings
from django.utils.crypto import get_random_string
from dj_utils import settings as u_settings
from dj_utils.image import image_get_format, is_image, adjust_image
from dj_utils.tools import datetime_to_dtstr, dtstr_to_datetime


def get_profile_configs(profile):
    """ Повертає налаштування для профіля """
    conf = copy.deepcopy(u_settings.DJU_IMG_UPLOAD_PROFILE_DEFAULT)
    if profile in u_settings.DJU_IMG_UPLOAD_PROFILES:
        conf.update(copy.deepcopy(u_settings.DJU_IMG_UPLOAD_PROFILES[profile]))
        for tn_i in xrange(len(conf['THUMBNAILS'])):
            t = conf['THUMBNAILS'][tn_i]
            conf['THUMBNAILS'][tn_i] = copy.deepcopy(u_settings.DJU_IMG_UPLOAD_PROFILE_THUMBNAIL_DEFAULT)
            conf['THUMBNAILS'][tn_i].update(t)
    return conf


def generate_filename(ext=None, label=None):
    """ Генерує ім'я фала. """
    if ext and not ext.startswith('.'):
        ext = '.' + ext
    if label:
        label = re.sub(r'[^a-z0-9_\-]', '', label, flags=re.I)[:60]
    return '{dtstr}_{rand}{label}{ext}'.format(
        dtstr=datetime_to_dtstr(),
        rand=get_random_string(4, 'abcdefghijklmnopqrstuvwxyz0123456789'),
        label='_' + label if label else '',
        ext=ext or '',
    )


def add_tmp_prefix_to_filename(filename):
    """ Додає префікс тимчасового файлу до імені файлу. """
    return u_settings.DJU_IMG_UPLOAD_TMP_PREFIX + filename


def add_thumb_suffix_to_filename(filename, label=None):
    """ Додає суфікс мініатюри до імені файла. Якщо суфікс вже є, тоді буде помилка ValueError. """
    return add_ending_to_filename(filename, '{}{}'.format(u_settings.DJU_IMG_UPLOAD_THUMB_SUFFIX, label or ''))


def add_ending_to_filename(filename, ending):
    """ Додає закінчення до імені файла. Якщо ім'я файлу має суфікс thumb, тоді буде помилка ValueError. """
    if u_settings.DJU_IMG_UPLOAD_THUMB_SUFFIX in filename:
        raise ValueError('Arg filename has thumb suffix "{suffix}": {fn}'.format(
            suffix=u_settings.DJU_IMG_UPLOAD_THUMB_SUFFIX, fn=filename
        ))
    ending = re.sub(r'[^a-z0-9_\-]', '', ending, flags=re.I)[:60]
    if ending:
        if not ending.startswith('_'):
            ending = '_' + ending
        fn, ext = os.path.splitext(filename)
        filename = '{fn}{ending}{ext}'.format(fn=fn, ending=ending, ext=ext)
    return filename


def get_subdir_for_filename(filename, default='other'):
    """ Повертає назву підпапки для файлу (dtstr[-2:]). """
    if filename.startswith(u_settings.DJU_IMG_UPLOAD_TMP_PREFIX):
        filename = filename[len(u_settings.DJU_IMG_UPLOAD_TMP_PREFIX):]
    m = re.match(r'^([a-z0-9]+?)_.+', filename)
    if m:
        return m.group(1)[-2:]
    return default


def get_filepath_of_url(url):
    """ Повертає шлях до файлу MEDIA по URL-адресі. """
    if url.startswith(settings.MEDIA_URL):
        url = url[len(settings.MEDIA_URL):]
    fn = os.path.join(settings.MEDIA_ROOT, os.path.normpath(url)).replace('\\', '/')
    return fn


def make_thumb_url(url, label=None, ext=None):
    """
    Генерує URL до мініатюри з URL основної картинки, label мініатюри та розширення.
    Якщо URL вже є на мініатюру, тоді повертає None.
    """
    path, filename = os.path.split(url)
    try:
        filename = add_thumb_suffix_to_filename(filename, label=label)
    except ValueError:
        return None
    if ext:
        if not ext.startswith('.'):
            ext = '.' + ext
        filename = os.path.splitext(filename)[0] + ext
    return os.path.join(path, filename).replace('\\', '/')


def gen_thumb_label(thumb_conf):
    """
    Генерує назву для мініатюри на основі налаштувань (розмірів мініатюри)
    """
    return 'x'.join(map(str, filter(None, thumb_conf['MAX_SIZE'])))


def remove_file_by_url(url, with_thumbs=True):
    """
    Видаляє файл по URL, якщо він знаходиться в папці MEDIA.
    with_thumbs - шукати і видаляти мініатюри файлу.
    """
    files = [get_filepath_of_url(url)]
    if with_thumbs:
        files.extend(get_thumbs_for_image(files[0]))
    for filepath in files:
        if os.path.isfile(filepath):
            os.remove(filepath)


def get_thumbs_for_image(filepath, label=None):
    """
    Повертає список шляхів на мініатюри для файлу filepath.
    Якщо переданий label, тоді буде додаткове відсіювання.
    """
    dir_path, filename = os.path.split(os.path.abspath(filepath))
    name = add_thumb_suffix_to_filename(os.path.splitext(filename)[0], label=label)
    pattern = os.path.join(dir_path, name).replace('\\', '/') + '*.*'
    return [fn.replace('\\', '/') for fn in glob.iglob(pattern)
            if os.path.splitext(fn)[1].lstrip('.').lower() in u_settings.DJU_IMG_UPLOAD_IMG_EXTS]


def move_to_permalink(url, with_thumbs=True):
    """
    Видаляє з файлу маркер тимчасовості.
    with_thumbs - шукати і застосовувати дану функцію на мініатюрах.
    """
    r = re.compile(r'^(.+?)(%s)(.+?)$' % u_settings.DJU_IMG_UPLOAD_TMP_PREFIX, re.I)
    url_m = r.match(url)
    if url_m:
        main_filename = get_filepath_of_url(url)
        if not os.path.isfile(main_filename):
            return url
        files = [main_filename]
        if with_thumbs:
            files.extend(get_thumbs_for_image(main_filename))
        for filepath in files:
            fn_m = r.match(filepath)
            if fn_m:
                try:
                    os.rename(filepath, fn_m.group(1) + fn_m.group(3))
                except EnvironmentError, e:
                    # pass  # todo додати логування помилки
                    raise e
            else:
                pass  # todo додати логування неспівпадіння імені файлу до шаблону
        url = url_m.group(1) + url_m.group(3)
    return url


def save_file(f, filename, path, tmp=False):
    """
    Збереження файлу.
    f - файл (об'єкт типу file)
    filename - назва файлу
    path - відносний шляд від папки DJU_IMG_UPLOAD_SUBDIR
    tmp - чи потрібно додати маркер тимчасового файла
    """
    path = path.strip('\\/')
    subdir = get_subdir_for_filename(filename)
    if tmp:
        filename = add_tmp_prefix_to_filename(filename)
    dir_path = os.path.join(settings.MEDIA_ROOT, u_settings.DJU_IMG_UPLOAD_SUBDIR, path, subdir).replace('\\', '/')
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, u_settings.DJU_CHMOD_DIR)
    fn_path = os.path.join(dir_path, filename).replace('\\', '/')
    with open(fn_path, 'wb') as t:
        f.seek(0)
        while True:
            buf = f.read(u_settings.DJU_RW_FILE_BUFFER_SIZE)
            if not buf:
                break
            t.write(buf)
    os.chmod(fn_path, u_settings.DJU_CHMOD_FILE)
    rel_dir_path = (os.path.join(u_settings.DJU_IMG_UPLOAD_SUBDIR, path, subdir) + '/').replace('\\', '/')
    return {
        'dir_path': dir_path,                                    # повний шлях до папки зі збереженим файлом
        'fn_path': fn_path,                                      # повний шлях до збереженого файлу
        'dir_url': settings.MEDIA_URL + rel_dir_path,            # абсолютний URL до папки зі збереженим файлом
        'fn_url': settings.MEDIA_URL + rel_dir_path + filename,  # абсолютний URL до збереженого файлу
        'rel_fn_path': rel_dir_path + filename,                  # відносний шлях до файлу (для збереження в БД)
    }


def remove_old_tmp_files(dirs, max_lifetime=(7 * 24), recursive=True):
    """
    Видалення старих тимчасових файлів.
    Запускати функцію періодично раз на добу або рідше.
    dirs -- список шляхів до папок, в яких треба зробити чистку (шлях має бути абсолютний)
    max_lifetime -- час життя файлу, в годинах.
    Запуск в консолі:
    # python manage.py shell
    > from dj_utils.upload import remove_old_tmp_files
    > remove_old_tmp_files(['images'], (4 * 24))
    """
    def get_files_recursive(path):
        for w_root, w_dirs, w_files in os.walk(path):
            for w_file in w_files:
                yield os.path.join(w_root, w_file).replace('\\', '/')

    def get_files(path):
        pattern = os.path.join(path, u_settings.DJU_IMG_UPLOAD_TMP_PREFIX + '*').replace('\\', '/')
        for filepath in glob.iglob(pattern):
            if os.path.isfile(filepath):
                yield filepath

    old_dt = datetime.datetime.utcnow() - datetime.timedelta(hours=max_lifetime)
    r = re.compile(
        r"^%s(?P<dtstr>[a-z0-9]+?)_[a-z0-9]+?(?:_.+?)?\.[a-z0-9]{1,8}$" % u_settings.DJU_IMG_UPLOAD_TMP_PREFIX,
        re.I
    )
    find_files = get_files_recursive if recursive else get_files
    total = removed = 0
    for dir_path in dirs:
        if not os.path.isdir(dir_path):
            continue
        for fn_path in find_files(dir_path):
            m = r.match(os.path.basename(fn_path))
            if not m:
                continue
            total += 1
            fdt = dtstr_to_datetime(m.group('dtstr'))
            if fdt and old_dt > fdt:
                os.remove(fn_path)
                removed += 1
    return removed, total


def remake_thumbs(profiles, clean=True):
    """
    Перестворює мініатюри для картинок згідно налаштувань.
    profiles - список з профілями, для яких треба застосувати дану функцію.
    clean - чи потрібно перед створення видалити ВСІ мініатюри для вказаних профілів.
    """
    def get_files_recursive(path):
        for w_root, w_dirs, w_files in os.walk(path):
            for w_file in w_files:
                yield os.path.join(w_root, w_file).replace('\\', '/')

    removed = created = 0
    for profile in profiles:
        conf = get_profile_configs(profile)
        profile_path = os.path.join(settings.MEDIA_ROOT, u_settings.DJU_IMG_UPLOAD_SUBDIR,
                                    conf['PATH']).replace('\\', '/')
        if clean:
            for fn in get_files_recursive(profile_path):
                if u_settings.DJU_IMG_UPLOAD_THUMB_SUFFIX in os.path.basename(fn):
                    os.remove(fn)
                    removed += 1
        for fn in get_files_recursive(profile_path):
            filename = os.path.basename(fn)
            if u_settings.DJU_IMG_UPLOAD_THUMB_SUFFIX in filename:
                continue  # пропускаємо файли, які мають суфікс мініатюри
            with open(fn, 'rb') as f:
                if not is_image(f, types=conf['TYPES']):
                    continue
                for tn_conf in conf['THUMBNAILS']:
                    tn_f = adjust_image(f, max_size=tn_conf['MAX_SIZE'], new_format=tn_conf['FORMAT'],
                                        jpeg_quality=tn_conf['JPEG_QUALITY'], fill=tn_conf['FILL'],
                                        stretch=tn_conf['STRETCH'], return_new_image=True)
                    tn_fn = os.path.splitext(filename)[0] + '.' + image_get_format(tn_f)
                    tn_fn = add_thumb_suffix_to_filename(tn_fn, tn_conf['LABEL'] or gen_thumb_label(tn_conf))
                    save_file(tn_f, tn_fn, conf['PATH'])
                    created += 1
    return removed, created
