# coding=utf-8
from __future__ import absolute_import
import copy
import datetime
import simplejson
from django.db import models
from django.utils.timezone import is_aware
from django.utils.translation import ugettext_lazy as _
from django.forms.fields import CharField
from django.forms.util import ValidationError


JSON_INVALID = ValidationError(_('Enter valid JSON.'))


class JSONFormField(CharField):
    def to_python(self, value):
        if not value and not self.required:
            return None
        if isinstance(value, basestring):
            try:
                value = simplejson.loads(value)
            except ValueError:
                raise JSON_INVALID
        return value


class JSONEncoder(simplejson.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date, time, datetime.
    """
    def default(self, o):
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError(_("JSON can't represent timezone-aware times."))
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        else:
            return super(JSONEncoder, self).default(o)


class JSONFieldBase(models.Field):
    __metaclass__ = models.SubfieldBase

    DEFAULT_USE_DECIMAL = False

    def __init__(self, *args, **kwargs):
        self.use_decimal = kwargs.pop('use_decimal', self.DEFAULT_USE_DECIMAL)
        self.dump_kwargs = {'cls': JSONEncoder,
                            'separators': (',', ':'),
                            'use_decimal': self.use_decimal}
        self.dump_kwargs.update(kwargs.pop('dump_kwargs', {}))
        self.load_kwargs = {'use_decimal': self.use_decimal}
        self.load_kwargs.update(kwargs.pop('load_kwargs', {}))
        if 'default' not in kwargs:
            kwargs['default'] = None
        elif isinstance(kwargs['default'], basestring):
            kwargs['default'] = simplejson.loads(kwargs['default'], **self.load_kwargs)
        if 'blank' not in kwargs:
            kwargs['blank'] = True
        super(JSONFieldBase, self).__init__(*args, **kwargs)

    def to_python(self, value):
        """ Convert string value to JSON """
        if isinstance(value, basestring):
            if value == '':
                return value
            try:
                return simplejson.loads(value, **self.load_kwargs)
            except ValueError:
                raise JSON_INVALID
        return value

    def get_prep_value(self, value):
        return self.get_db_prep_value(value, None)

    def get_db_prep_value(self, value, connection, prepared=False):
        """ Convert JSON object to a string """
        if isinstance(value, basestring):
            return value
        if self.null and value is None:
            return None
        return simplejson.dumps(value, **self.dump_kwargs)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value, None)

    def value_from_object(self, obj):
        value = super(JSONFieldBase, self).value_from_object(obj)
        if self.null and value is None:
            return None
        return self.dumps_for_display(value)

    def dumps_for_display(self, value):
        return simplejson.dumps(value, **self.dump_kwargs)

    def formfield(self, **kwargs):
        if 'form_class' not in kwargs:
            kwargs['form_class'] = JSONFormField
        field = super(JSONFieldBase, self).formfield(**kwargs)
        if not field.help_text:
            field.help_text = _('JSON data')
        return field

    def get_default(self):
        if self.has_default():
            if callable(self.default):
                return self.default()
            if not isinstance(self.default, basestring):
                return self.dumps_for_display(self.default)
            return copy.deepcopy(self.default)
        return super(JSONFieldBase, self).get_default()


class JSONField(JSONFieldBase, models.TextField):
    def dumps_for_display(self, value):
        kwargs = self.dump_kwargs.copy()
        kwargs.update({'indent': 4,
                       'separators': (',', ': '),
                       'sort_keys': True})
        return simplejson.dumps(value, **kwargs)


class JSONCharField(JSONFieldBase, models.CharField):
    pass
