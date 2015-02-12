# coding=utf-8
from __future__ import absolute_import
import copy
import random
from django.conf import settings
from django.db import models, IntegrityError
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _
from dj_utils.db import get_object_or_None
from dj_utils.fields import JSONField


class PrivateUrlManager(models.Manager):
    def get_or_none(self, action, token):
        return get_object_or_None(self.select_related('user'), action=action, token=token)

    def add(self, action, user=None, expire=None, data=None, used_limit=1, auto_delete=False, token_size=None):
        """
        Створює новий об'єкт PrivateUrl
        :param action: назва події (slug)
        :param user: user or None
        :param expire: datetime or None
        :param data: dict or None
        :param used_limit: number (default 1)
        :param auto_delete: bool (default False)
        :param token_size: tuple (min, max) or number or None
        :return: new saved object
        """
        max_tries, n = 20, 0
        if data:
            data = copy.deepcopy(data)
        while True:
            try:
                return self.create(user=user, action=action, token=self.model.generate_token(size=token_size),
                                   expire=expire, data=data, used_limit=used_limit, auto_delete=auto_delete)
            except IntegrityError:
                n += 1
                if n > max_tries:
                    raise RuntimeError("It can't make PrivateUrl object (action={}, token_size={})".format(
                        action, token_size
                    ))
                continue


class PrivateUrl(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), null=True, blank=True)
    action = models.SlugField(verbose_name=_('action'), max_length=24, db_index=True)
    token = models.SlugField(verbose_name=_('token'), max_length=64)
    expire = models.DateTimeField(verbose_name=_('expire'), null=True, blank=True, db_index=True)
    data = JSONField(verbose_name=_('data'), use_decimal=True)
    created = models.DateTimeField(verbose_name=_('created'), auto_now_add=True, db_index=True)
    used_limit = models.PositiveIntegerField(verbose_name=_('used limit'), default=1, help_text=_('Set 0 to unlimit.'))
    used_counter = models.PositiveIntegerField(verbose_name=_('used counter'), default=0)
    first_used = models.DateTimeField(verbose_name=_('first used'), null=True, blank=True)
    last_used = models.DateTimeField(verbose_name=_('last used'), null=True, blank=True)
    auto_delete = models.BooleanField(verbose_name=_('auto delete'), default=False, db_index=True,
                                      help_text=_("Delete object if it can no longer be used."))

    objects = PrivateUrlManager()

    class Meta:
        db_table = 'dju_privateurl'
        ordering = ('-created',)
        unique_together = ('action', 'token')
        verbose_name = _('private url')
        verbose_name_plural = _('privete urls')

    def is_available(self, dt=None):
        """
        Повертає True, якщо об'єкт може бути використаний
        """
        if self.expire and self.expire <= (dt or timezone.now()):
            return False
        if self.used_limit and self.used_limit <= self.used_counter:
            return False
        return True

    def used_counter_inc(self):
        now = timezone.now()
        self.used_counter += 1
        if self.auto_delete and not self.is_available(dt=now):
            return self.delete()
        uf = {'used_counter', 'last_used'}
        if not self.first_used:
            self.first_used = now
            uf.add('first_used')
        self.last_used = now
        self.save(update_fields=uf)

    @staticmethod
    def generate_token(size=None):
        """
        Генерує новий унікальний токен для action.
        size = (мінімальни розмір, максимальний розмір) або просто розмір
        """
        if size is None:
            size = (40, 64)
        if isinstance(size, (list, tuple)):
            assert len(size) == 2 and 0 < size[0] < 64 and 2 < size[1] <= 64 and size[0] < size[1]
            random.seed(get_random_string(length=100))
            _size = random.randint(*size)
        else:
            assert 0 < size <= 64
            _size = size
        return get_random_string(length=_size)
