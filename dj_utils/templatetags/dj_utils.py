# coding=utf-8
from __future__ import absolute_import
import simplejson
from django import template
from django.template.loader import get_template
from django.http import QueryDict
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.core.cache.utils import make_template_fragment_key
from django.core.cache import cache
from dj_utils import gravatar
from dj_utils.tcache import cache_set
from dj_utils.http import full_url, get_urls_for_langs
from dj_utils.tools import long_number_readable
from dj_utils.upload import make_thumb_url


register = template.Library()


@register.filter
def of_key(value, arg):
    try:
        return value.get(arg, '')
    except AttributeError:
        return ''


@register.filter
def of_strkey(value, arg):
    try:
        return value.get(str(arg), '')
    except AttributeError:
        return ''


@register.filter
def of_index(value, arg):
    return value[int(arg)]


@register.filter
def is_in(value, arg):
    """
    {% if tag|is_in:'div|p|span' %}is block tag{% endif %}
    {% if tag|is_in:tags_list %}is block tag{% endif %}
    """
    if isinstance(arg, basestring):
        arg = arg.split('|')
    return value in arg


@register.filter
def items_val_sort_dict(value, arg=None):
    items = value.items()
    items.sort(key=lambda t: t[1], reverse=bool(arg))
    return items


@register.filter
def items_key_sort_dict(value, arg=None):
    items = value.items()
    items.sort(key=lambda t: t[0], reverse=bool(arg))
    return items


class CaptureasNode(template.Node):
    def __init__(self, nodelist, args):
        self.nodelist = nodelist
        self.varname = args[1]
        self.assign_and_print = len(args) > 2 and bool(args[2])

    def render(self, context):
        output = self.nodelist.render(context)
        context[self.varname] = output
        return output if self.assign_and_print else ''


@register.tag
def captureas(parser, arg):
    """
    example: {% captureas myvar 1 %}content...{% endcaptureas %} - {{ myvar }}
    result: content... - content...

    example: {% captureas myvar %}content...{% endcaptureas %} - {{ myvar }}
    result: - content...
    """
    args = arg.contents.split()
    if not 2 <= len(args) <= 3:
        raise template.TemplateSyntaxError('"captureas" node requires a variable name and/or assign only')
    nodelist = parser.parse(('endcaptureas',))
    parser.delete_first_token()
    return CaptureasNode(nodelist, args)


class StripNode(template.Node):
    def __init__(self, nodelist, args):
        if len(args) > 2:
            raise template.TemplateSyntaxError("'%s' tag can have one parameter" % args[0])
        self.nodelist = nodelist
        self.separator = args[1][1:-1] if len(args) == 2 else ' '
        self.separator = self.separator.replace('{\\n}', '\n')

    def render(self, context):
        output = self.nodelist.render(context)
        return self.separator.join(filter(bool, [line.strip() for line in output.splitlines()]))


@register.tag
def strip(parser, arg):
    """
    example:
        {% strip '<br>' %}
            content...
            content...
        {% endstrip %}
    result:
        content...<br>content...
    arg special symbols: {\n} = \n
    """
    nodelist = parser.parse(('endstrip',))
    parser.delete_first_token()
    return StripNode(nodelist, arg.split_contents())


class IncludeNode(template.Node):
    def __init__(self, template_name):
        self.template_name = template_name

    def render(self, context):
        try:
            included_template = get_template(self.template_name).render(context)
        except template.TemplateDoesNotExist:
            included_template = ''
        return included_template


@register.tag
def include_silently(parser, token):
    """
    Include template if it exists.
    If it doesn't exist then will not raise any exception.
    {% include_silently "mytemplate.html" %}
    """
    try:
        tag_name, template_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('%r tag requires a single argument' % token.contents.split()[0])
    return IncludeNode(template_name[1:-1])


class RecurseNode(template.Node):
    def __init__(self, template_nodes, items_var, children_attr):
        self.template_nodes = template_nodes
        self.items_var = items_var
        self.children_attr = children_attr

    def _render(self, context, item, level=1):
        t = []
        context.push()
        if hasattr(item, self.children_attr):
            children = getattr(item, self.children_attr)
            if callable(children):
                children = children()
        else:
            children = item.get(self.children_attr)
        for child in children:
            t.append(self._render(context, child, level=level + 1))
        context['item'] = item
        context['subitems'] = mark_safe(''.join(t))
        context['recurse_level'] = level
        rendered = self.template_nodes.render(context)
        context.pop()
        return rendered

    def render(self, context):
        return ''.join(self._render(context, item) for item in self.items_var.resolve(context))


@register.tag
def recurse(parser, token):
    """
    Iterate recurse data structure.
    <ul>
        {% recurse items %}
            <li>
                {{ item.name }}
                {% if item.children %}
                    <ul>
                        {{ subitems }}
                    </ul>
                {% endif %}
            </li>
        {% endrecurse %}
    </ul>
    If subelements found in other key/attribute/method then need set its name (default is 'children'):
        {% recurse items 'subitems' %}
    Also available depth level in variable {{ recurse_level }} (starting of 1)
    """
    params = token.contents.split()
    if not 2 <= len(params) <= 3:
        raise template.TemplateSyntaxError('%s parameters error' % params[0])
    template_nodes = parser.parse(('endrecurse',))
    parser.delete_first_token()
    return RecurseNode(template_nodes,
                       template.Variable(params[1]),
                       (params[2][1:-1] if len(params) == 3 else 'children'))


@register.filter
def humanize_long_number(value):
    """
    Convert big integer (>=999) to readable form.
    """
    return long_number_readable(value)

    
@register.filter(is_safe=False)
def subtract(value, arg):
    """ Subtract the arg of the value. """
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        try:
            return value - arg
        except TypeError:
            return ''


@register.assignment_tag
def assign(value):
    """
    Setting value to a variable.
    {% assign obj.get_full_name as obj_full_name %}
    """
    return value


@register.assignment_tag
def assign_format_str(string, *args, **kwargs):
    """
    Форматує стрічку і зберігає її в змінній.
    Приймає як нумеровані так і названі аргументи.
    {% assign_format_str 'contacts_{lang}.html' lang=LANGUAGE_CODE as tpl_name %}
    {% include tpl_name %}
    """
    return string.format(*args, **kwargs)


@register.filter
def tojson(value):
    return simplejson.dumps(value)


@register.inclusion_tag(('paginator.html', 'dj_utils/tags/paginator.html'), takes_context=True)
def paginator(context, page, leading=8, out=3, adjacent=3, sep='...'):
    """
    Вивід навігатора пагінатора
    Приклад 1: <<_1_2 3 4 5 6 7 8 9 ... 55 56 57 >>
    leading -- 9 (1..9)
    out     -- 3 (55..57)
    Приклад 2: << 1 2 3 ... 23 24 25 26_27_28 29 30 31 ... 55 56 57 >>
    adjacent = 4 (23..26, 28..31)
    todo продокументувати  параметри
    """
    leading_pages, out_left_pages, out_right_pages, pages = [], [], [], []
    num_pages = page.paginator.num_pages
    is_paginated = num_pages > 1
    if is_paginated:
        if num_pages < leading:
            leading_pages = [x for x in xrange(1, leading) if x <= num_pages]
        elif page.number <= leading - 1:
            leading_pages = [x for x in xrange(1, leading + 1)]
            out_right_pages = [x + num_pages for x in xrange(-out + 1, 1) if x + num_pages > leading]
        elif page.number > num_pages - leading + 1:
            leading_pages = [x for x in xrange(num_pages - leading + 1, num_pages + 1) if x <= num_pages]
            out_left_pages = [x for x in xrange(1, out + 1) if num_pages - x >= leading]
        else:
            leading_pages = [x for x in xrange(page.number - adjacent, page.number + adjacent + 1)]
            out_right_pages = [x + num_pages for x in xrange(-out + 1, 1)]
            out_left_pages = [x for x in xrange(1, out + 1)]
    if out_left_pages:
        pages.extend(out_left_pages)
        pages.append(sep)
    pages.extend(leading_pages)
    if out_right_pages:
        pages.append(sep)
        pages.extend(out_right_pages)
    return {
        'page': page,
        'pages': pages,
        'is_paginated': is_paginated,
        'separator': sep,
        'request': context['request'],
        'param_name': page.param_name if hasattr(page, 'param_name') else 'page',
    }


@register.filter
def is_str(value, arg=None):
    return force_unicode(value) == force_unicode(arg)


@register.filter
def html_encode(value):
    """
    Перекодовує текст в символи спецсимволи HTML.
    Варто використовуати для приховування email від спам-ботів, наприклад:
        <a href="{{ 'mailto:my@example.com'|html_encode }}">{{ 'my@example.com'|html_encode }}</a>
    Результат:
        <a href="&#109;&#97;&#105;&#108;&#116;&#111;&#58;&#109;&#121;&#64;...">&#109;&#121;&#64;&#101;&#120;...</a>
    """
    return mark_safe(''.join('&#%d;' % ord(c) for c in value))


class CacheNode(template.Node):
    def __init__(self, nodelist, expire_time_var, fragment_name, vary_on, tags):
        self.nodelist = nodelist
        self.expire_time_var = expire_time_var
        self.fragment_name = fragment_name
        self.vary_on = vary_on
        self.tags = tags

    def get_tags(self, context):
        if self.tags:
            tags = self.tags.resolve(context)
            if isinstance(tags, basestring):
                tags = [tag.strip() for tag in tags.split(',')]
            elif not isinstance(tags, (list, tuple, set)):
                raise template.TemplateSyntaxError('"tcache" tag variable "tags" invalid')
            return filter(None, tags) or None

    def render(self, context):
        try:
            expire_time = self.expire_time_var.resolve(context)
        except template.VariableDoesNotExist:
            raise template.TemplateSyntaxError('"tcache" tag got an unknown variable: %r' % self.expire_time_var.var)
        try:
            expire_time = int(expire_time)
        except (ValueError, TypeError):
            raise template.TemplateSyntaxError('"tcache" tag got a non-integer timeout value: %r' % expire_time)
        vary_on = [var.resolve(context) for var in self.vary_on]
        cache_key = make_template_fragment_key(self.fragment_name, vary_on)
        value = cache.get(cache_key)
        if value is None:
            value = self.nodelist.render(context)
            cache_set(cache_key, value, timeout=expire_time, tags=self.get_tags(context))
        return value


@register.tag
def tcache(parser, token):
    """
    This will cache the contents of a template fragment for a given amount
    of time with support tags.

    Usage::

        {% load tcache %}
        {% tcache [expire_time] [fragment_name] [tags='tag1,tag2'] %}
            .. some expensive processing ..
        {% endtcache %}

    This tag also supports varying by a list of arguments::

        {% load tcache %}
        {% tcache [expire_time] [fragment_name] [var1] [var2] .. [tags=tags] %}
            .. some expensive processing ..
        {% endtcache %}

    Each unique set of arguments will result in a unique cache entry.
    """
    nodelist = parser.parse(('endtcache',))
    parser.delete_first_token()
    tokens = token.split_contents()
    if len(tokens) < 3:
        raise template.TemplateSyntaxError("'%r' tag requires at least 2 arguments." % tokens[0])
    tags = None
    if len(tokens) > 3 and 'tags=' in tokens[-1]:
        tags = parser.compile_filter(tokens[-1][5:])
        del tokens[-1]
    return CacheNode(nodelist,
        parser.compile_filter(tokens[1]),
        tokens[2],  # fragment_name can't be a variable.
        [parser.compile_filter(token) for token in tokens[3:]],
        tags
    )


@register.filter
def gravatar_ava_url(value, arg=None):
    return gravatar.get_ava_url(value, arg)


@register.filter
def gravatar_profile_url(value):
    return gravatar.get_profile_url(value)


def _url_get_amps(token=None):
    l, r, amp = '', '', u'&amp;'
    if token and len(token) > 1:
        token = token.strip()
        if token.startswith('&'):
            l = amp
        if token.endswith('&'):
            r = amp
        token = token.strip('&')
    return token, l, r


def _url_getvars(context, token_=None, type_=None):
    token, l, r = _url_get_amps(token_)
    gv = ''
    if type_:
        w, wo = type_ == 'with', type_ == 'without'
        if not w and not wo:
            type_ = None
        else:
            lst = [p.strip() for p in token.split(',') if p.strip()]
            if w and not lst:
                pass
            elif wo and not lst:
                type_ = None
            else:
                params, gets = QueryDict('', mutable=True), context['request'].GET
                if w:
                    q = lambda x: x
                else:
                    q = lambda x: not x
                for key in gets:
                    if q(key in lst):
                        params.setlist(key, gets.getlist(key))
                gv = params.urlencode()
    if not type_:
        gv = context['request'].GET.urlencode()
    if gv:
        gv = l + gv + r
    return gv


@register.simple_tag(takes_context=True)
def url_getvars(context, token=None):
    return mark_safe(_url_getvars(context, token))


@register.simple_tag(takes_context=True)
def url_getvars_with(context, token):
    return mark_safe(_url_getvars(context, token, 'with'))


@register.simple_tag(takes_context=True)
def url_getvars_without(context, token):
    return mark_safe(_url_getvars(context, token, 'without'))


@register.simple_tag
def full_url_prefix(secure=None):
    return mark_safe(full_url(secure=secure))


@register.assignment_tag(takes_context=True, name='get_urls_for_langs')
def get_urls_for_langs_(context):
    """
    Повертає словник з посиланням на дану сторінку для різних мов.
    В контексті має бути request.
    {% get_urls_for_langs as urls %}
    {'en': '/about-us', 'uk': '/ua/pro-nas'}
    """
    return get_urls_for_langs(context['request'])


@register.assignment_tag(name='make_thumb_url')
def make_thumb_url_(url, label=None, ext=None):
    return make_thumb_url(url, label=label, ext=ext) or url
