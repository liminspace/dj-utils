# coding=utf-8
import os
from django.conf import settings


# ------------
# COMMON SETTINGS
# ------------
USE_HTTPS = getattr(settings, 'USE_HTTPS', False)

LOG_DIR = getattr(settings, 'LOG_DIR', os.path.join(settings.BASE_DIR, 'logs').replace('\\', '/'))

EMAIL_RETURN_PATH = getattr(settings, 'EMAIL_RETURN_PATH', None)
EMAIL_REPLY_TO = getattr(settings, 'EMAIL_REPLY_TO', None)  # list of emails

LANGUAGE_CODES = tuple(t[0] for t in settings.LANGUAGES)


# ------------
# SENDING EMAIL
# ------------
DJU_EMAIL_DOMAIN_BLACK_LIST = getattr(settings, 'DJU_EMAIL_DOMAIN_BLACK_LIST', (
    'mailinator.com', '10minutemail.com', 'spambog.com', 'tempinbox.com', 'mailmetrash.com',
    'tempemail.net', 'yopmail.com', 'sharklasers.com', 'guerrillamailblock.com', 'guerrillamail.com',
    'guerrillamail.net', 'guerrillamail.biz', 'guerrillamail.org', 'guerrillamail.de', 'spam4.me', 'spam.su',
    'inboxed.im', 'inboxed.pw', 'gomail.in', 'tokem.co', 'nomail.pw', 'yanet.me', 'powered.name', 'shut.ws',
    'vipmail.pw', 'powered.im', 'linuxmail.so', 'secmail.pw', 'shut.name', 'freemail.ms', 'mailforspam.com',
    'uroid.com', 'rmqkr.net',
))

DJU_EMAIL_DEFAULT_CONTEXT = getattr(settings, 'DJU_EMAIL_DEFAULT_CONTEXT', 'dj_utils.context_processors.email_default')


# ------------
# IMAGES UPLOAD
# ------------
# path that relatively MEDIA. For example: 'dir' or 'dir1/dir2'
DJU_IMG_UPLOAD_SUBDIR = getattr(settings, 'DJU_IMG_UPLOAD_SUBDIR', 'upload-img')

# default profile (other profiles will extend from this if they won't set some parameters)
DJU_IMG_UPLOAD_PROFILE_DEFAULT = {
    'PATH': 'common',                 # підпапка в DJU_UPLOAD_SUBDIR ('dir', 'dir1/dir2')
    'TYPES': ('GIF', 'JPEG', 'PNG'),  # формати, які підтримуються
    'MAX_SIZE': (800, 800),           # максимальний розмір (ширина і висота) може мати одне з значень None (авто)
    'FILL': False,                    # чи зображення має бути заповненим при обрізці (інакше буде вписане)
    'STRETCH': False,                 # чи розтягувати зображення, якщо воно замале
    'FORMAT': None,                   # в якому форматі зберігати (якщо None, тоді буде формат оригіналу)
    'JPEG_QUALITY': 95,               # якість JPEG
    'THUMBNAILS': [],                 # набір налаштувань мініатюр
}

# налаштування для мініатюр по замовчуванню
DJU_IMG_UPLOAD_PROFILE_THUMBNAIL_DEFAULT = {
    'LABEL': None,                # назва мініатюри (якщо None, тоді буде генеруватись автоматично (типу '50x60'))
    'MAX_SIZE': (160, 160),
    'FILL': True,
    'STRETCH': True,
    'FORMAT': None,
    'JPEG_QUALITY': 90,
}

# profiles
DJU_IMG_UPLOAD_PROFILES = getattr(settings, 'DJU_IMG_UPLOAD_PROFILES', {})

DJU_IMG_UPLOAD_TMP_PREFIX = getattr(settings, 'DJU_IMG_UPLOAD_TMP_PREFIX', '__tmp__')
DJU_IMG_UPLOAD_THUMB_SUFFIX = getattr(settings, 'DJU_IMG_UPLOAD_THUMB_SUFFIX', '__thumb__')
DJU_IMG_UPLOAD_IMG_EXTS = ('jpeg', 'jpg', 'png', 'gif')  # розширення файлів зображень
DJU_IMG_USE_JPEGTRAN = getattr(settings, 'DJU_IMG_USE_JPEGTRAN', False)  # використання утиліти jpegtran (лише Linux)
# використання утиліти convert (ImageMagick) (лише Linux)
DJU_IMG_CONVERT_JPEG_TO_RGB = getattr(settings, 'DJU_IMG_CONVERT_JPEG_TO_RGB', False)


# ------------
# EMAIL DEBUGGING
# ------------
DJU_EMAIL_DEBUG_IN_CONSOLE = getattr(settings, 'DJU_EMAIL_DEBUG_IN_CONSOLE', True)
DJU_EMAIL_DEBUG_IN_FILES = getattr(settings, 'DJU_EMAIL_DEBUG_IN_FILES', True)
DJU_EMAIL_DEBUG_PATH = getattr(settings, 'DJU_EMAIL_DEBUG_PATH',
                               os.path.join(LOG_DIR, 'debug_email').replace('\\', '/'))


# ------------
# GRAVATAR
# ------------
DJU_GRAVATAR_DEFAULT_SIZE = getattr(settings, 'DJU_GRAVATAR_DEFAULT_SIZE', 50)
# 404, mm, identicon, monsterid, wavatar, retro, blank, http://mysite.com/default.jpg
DJU_GRAVATAR_DEFAULT_IMAGE = getattr(settings, 'DJU_GRAVATAR_DEFAULT_IMAGE', 'mm')
DJU_GRAVATAR_RATING = getattr(settings, 'DJU_GRAVATAR_RATING', 'g')  # g, pg, r, x
DJU_GRAVATAR_SECURE = getattr(settings, 'DJU_GRAVATAR_SECURE', False)


# ------------
# FILESYSTEM PERMISSIONS
# ------------
DJU_CHMOD_DIR = getattr(settings, 'DJU_CHMOD_DIR', 0o775)    # права на створені папки
DJU_CHMOD_FILE = getattr(settings, 'DJU_CHMOD_DIR', 0o664)   # права на створені файли


# ------------
# OTHER
# ------------
DJU_RW_FILE_BUFFER_SIZE = getattr(settings, 'DJU_RW_FILE_BUFFER_SIZE', 8192)  # розмір буферу при читанні/запису файлів
