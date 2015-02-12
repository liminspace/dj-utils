# coding=utf-8
from __future__ import absolute_import
from django.contrib import admin
from dj_utils.privateurl.models import PrivateUrl
from django.utils.translation import gettext, ugettext_lazy as _


class PrivateUrlAdmin(admin.ModelAdmin):
    list_display = ('action_with_token', 'user', 'created', 'expire', 'used', 'available')
    list_filter = ('action',)
    list_select_related = ('user',)
    raw_id_fields = ('user',)

    def __init__(self, *args, **kwargs):
        super(PrivateUrlAdmin, self).__init__(*args, **kwargs)

    def action_with_token(self, obj):
        return '{}/{}'.format(obj.action, obj.token)
    action_with_token.short_description = _('action/token')

    def used(self, obj):
        return '{} / {}'.format(obj.used_counter, obj.used_limit or gettext('unlimit'))
    used.short_description = _('used')

    def available(self, obj):
        return obj.is_available()
    used.short_description = _('available')
    available.boolean = True


admin.site.register(PrivateUrl, PrivateUrlAdmin)
