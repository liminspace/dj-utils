# coding=utf-8
from __future__ import absolute_import
import os
from dj_utils.http import send_json
from django.utils.translation import ugettext as _
from dj_utils.image import image_get_format, adjust_image, is_image
from dj_utils.upload import (get_profile_configs, generate_filename, add_thumb_suffix_to_filename, save_file,
                             gen_thumb_label)


def upload_image(request):
    """
    Вюха, яка зберігає завантажений файл.
    Структура запиту:
        FILES
            image: файл зображення
        POST DATA
            profile: назва профілю (для визначення налаштувань збреження) (опціонально)
            label: додаток до назви файлу при збереженні (опіонально)
    Структура відповіді:
        Тип відповіді: JSON
        {
            'upload': {
                'url': 'url до збереженого файлу',
                'url_to_save': 'url відносто папки MEDIA (для збереження в БД)',
                'thumbnails': [  # список з мініатюрами
                    {
                        'url': 'url до збереженого файлу',
                        'url_to_save': 'url відносто папки MEDIA (для збереження в БД)'
                    },
                    ...
                ]
            }
        }
    """
    if 'image' not in request.FILES:
        return send_json({'error': _('Uploaded file not found.')})
    conf = get_profile_configs(request.REQUEST.get('profile'))
    f = request.FILES['image']
    if not is_image(f, types=conf['TYPES']):
        return send_json({
            'error': _('Format of downloaded file is not allowed. Allowed: %s.') % ', '.join(conf['TYPES'])
        })
    adjust_image(f, max_size=conf['MAX_SIZE'], new_format=conf['FORMAT'],
                 jpeg_quality=conf['JPEG_QUALITY'], fill=conf['FILL'], stretch=conf['STRETCH'])
    filename = generate_filename(ext=image_get_format(f), label=request.POST.get('label'))
    saved_file = save_file(f, filename, conf['PATH'], tmp=True)
    data = {'upload': {'url': saved_file['fn_url'],
                       'url_to_save': saved_file['rel_fn_path']}}
    thumb_data = []
    for tn_conf in conf['THUMBNAILS']:
        tn_f = adjust_image(f, max_size=tn_conf['MAX_SIZE'], new_format=tn_conf['FORMAT'],
                            jpeg_quality=tn_conf['JPEG_QUALITY'], fill=tn_conf['FILL'], stretch=tn_conf['STRETCH'],
                            return_new_image=True)
        tn_filename = os.path.splitext(filename)[0] + '.' + image_get_format(tn_f)
        tn_filename = add_thumb_suffix_to_filename(tn_filename, tn_conf['LABEL'] or gen_thumb_label(tn_conf))
        saved_tn = save_file(tn_f, tn_filename, conf['PATH'], tmp=True)
        thumb_data.append({'url': saved_tn['fn_url'],
                           'url_to_save': saved_tn['rel_fn_path']})
    data['upload']['thumbnails'] = thumb_data
    return send_json(data)
