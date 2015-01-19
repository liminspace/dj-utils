# coding=utf-8
from __future__ import absolute_import
import os
from dj_utils.http import send_json
from django.utils.translation import ugettext as _
from dj_utils.image import image_get_format, adjust_image
from dj_utils.upload import get_profile_configs, generate_filename, add_thumb_suffix_to_filename, save_file


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
    file_format = image_get_format(f)
    if not file_format or file_format.upper() not in conf['TYPES']:
        return send_json({
            'error': _('Format of downloaded file is not allowed. Allowed: %s.') % ', '.join(conf['TYPES'])
        })
    adjust_image(f, max_size=conf['MAX_SIZE'], new_format=conf['FORMAT'],
                 jpeg_quality=conf['JPEG_QUALITY'], fill=conf['FILL'], stretch=conf['STRETCH'])
    filename = generate_filename(ext=image_get_format(f), label=request.POST.get('label'))
    saved_file = save_file(f, filename, conf['PATH'])
    data = {'upload': {'url': saved_file['fn_url'],
                       'url_to_save': saved_file['rel_fn_path']}}
    thumb_data = []
    for sn_conf in conf['THUMBNAILS']:
        sn_f = adjust_image(f, max_size=sn_conf['MAX_SIZE'], new_format=sn_conf['FORMAT'],
                            jpeg_quality=sn_conf['JPEG_QUALITY'], fill=sn_conf['FILL'], stretch=sn_conf['STRETCH'],
                            return_new_image=True)
        sn_filename = os.path.splitext(filename)[0] + '.' + image_get_format(sn_f)
        label = sn_conf['LABEL'] or ''
        if not label:
            label = 'x'.join(map(str, filter(None, sn_conf['MAX_SIZE'])))
        sn_filename = add_thumb_suffix_to_filename(sn_filename, label)
        saved_sn = save_file(sn_f, sn_filename, conf['PATH'])
        thumb_data.append({'url': saved_sn['fn_url'],
                           'url_to_save': saved_sn['rel_fn_path']})
    data['upload']['thumbnails'] = thumb_data
    return send_json(data)
