import time
try:
    from html import unescape  # python 3.4+
except ImportError:
    from HTMLParser import HTMLParser  # python 2.x
    unescape = HTMLParser().unescape

from django.contrib.sites.models import Site
from django.core.paginator import Paginator
from django.http import QueryDict
from django.template import Template, Context, TemplateSyntaxError
from django.test import TestCase
from django.utils.html import escape
from dj_utils import settings as u_settings


class TestTemplatetagsDjUtils(TestCase):
    class R(object):
        def __init__(self, query):
            self.GET = QueryDict(query)

    def get_tpl_f(self, tpl, context=None):
        return lambda: Template('{% load dj_utils %}' + tpl).render(Context(context))

    def test_of_index(self):
        t = self.get_tpl_f("{{ var|of_index:2 }}", {'var': [1, 2, 3, 4]})
        self.assertEqual(t(), '3')

        t = self.get_tpl_f("{{ var|of_index:'2' }}", {'var': [1, 2, 3, 4]})
        self.assertEqual(t(), '3')

        t = self.get_tpl_f("{{ var|of_index:9 }}", {'var': [1, 2, 3, 4]})
        self.assertEqual(t(), '')

    def test_dict_items_sort_by_val(self):
        t = self.get_tpl_f(
            "{% for k, v in var|dict_items_sort_by_val %}{{ k }}{{ v }}{% endfor %}",
            {'var': {'1': 'a', '2': 'b', '3': 'c', '4': 'd', '5': 'e'}})
        self.assertEqual(t(), "1a2b3c4d5e")

        t = self.get_tpl_f(
            "{% for k, v in var|dict_items_sort_by_val %}{{ k }}{{ v }}{% endfor %}",
            {'var': None})
        self.assertEqual(t(), '')

    def test_dict_items_sort_by_key(self):
        t = self.get_tpl_f(
            "{% for k, v in var|dict_items_sort_by_key %}{{ k }}{{ v }}{% endfor %}",
            {'var': {'1': 'a', '2': 'b', '3': 'c', '4': 'd', '5': 'e'}})
        self.assertEqual(t(), "1a2b3c4d5e")

        t = self.get_tpl_f(
            "{% for k, v in var|dict_items_sort_by_key %}{{ k }}{{ v }}{% endfor %}",
            {'var': None})
        self.assertEqual(t(), '')

    def test_make_thumb_url(self):
        suf = u_settings.DJU_IMG_UPLOAD_THUMB_SUFFIX

        t = self.get_tpl_f("{% make_thumb_url '/media/a/b/abc.jpeg' as v %}{{ v }}")
        self.assertEqual(t(), '/media/a/b/abc{suf}.jpeg'.format(suf=suf))

        t = self.get_tpl_f(
            "{% make_thumb_url '/media/a/b/abc{suf}.jpeg' as v %}{{ v }}".replace('{suf}', suf)
        )
        self.assertEqual(t(), '/media/a/b/abc{suf}.jpeg'.format(suf=suf))

        t = self.get_tpl_f("{% make_thumb_url '/media/a/b/abc.dat' label='tst' ext='png' as v %}{{ v }}")
        self.assertEqual(t(), '/media/a/b/abc{suf}tst.png'.format(suf=suf))

        t = self.get_tpl_f("{% make_thumb_url '/media/a/b/abc.dat' label='tst' ext='png' as v %}{{ v }}")
        self.assertEqual(t(), '/media/a/b/abc{suf}tst.png'.format(suf=suf))

        t = self.get_tpl_f("{% make_thumb_url '/media/a/b/abc.dat' label='tst' ext='.png' as v %}{{ v }}")
        self.assertEqual(t(), '/media/a/b/abc{suf}tst.png'.format(suf=suf))
