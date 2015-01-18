# coding=utf-8
from __future__ import absolute_import
import mimetypes
import os
import urllib
import urlparse
import simplejson
from django.utils import translation
from django.http import HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import resolve_url
from django.core.servers.basehttp import FileWrapper
from django.core.urlresolvers import resolve
from dj_utils import settings as u_settings


def resolve_url_ext(to, params_=None, anchor_=None, *args, **kwargs):
    """ Advanced resolve_url which can includes GET-parameters and anchor. """
    url = resolve_url(to, *args, **kwargs)
    if params_:
        url += '?' + urllib.urlencode(params_)
    if anchor_:
        url += '#' + anchor_
    return url


def send_file(filepath, filename=None, content_type=None, encoding=None):
    if filename is None:
        filename = os.path.basename(filepath)
    if content_type is None:
        content_type, encoding = mimetypes.guess_type(filepath)
    response = HttpResponse(FileWrapper(file(filepath, 'rb')), content_type=content_type)
    response['Content-Disposition'] = "attachment; filename*=UTF-8''%s" % urllib.quote(filename.encode('utf-8'))
    response['Content-Length'] = os.stat(filepath).st_size
    if encoding is not None:
        response['Content-Encoding'] = encoding
    return response


def send_json(data, content_type='application/json', status=200):
    return HttpResponse(simplejson.dumps(data), content_type=content_type, status=status)


def send_jsonp(data, f='jsonpCallback'):
    return HttpResponse('%s(%s);' % (f, simplejson.dumps(data)), content_type='application/javascript')


def redirect_ext(to, params_=None, anchor_=None, permanent_=False, *args, **kwargs):
    """ Advanced redirect which can includes GET-parameters and anchor. """
    if permanent_:
        redirect_class = HttpResponsePermanentRedirect
    else:
        redirect_class = HttpResponseRedirect
    return redirect_class(resolve_url_ext(to, params_, anchor_, *args, **kwargs))


def change_url_query_params(url, params):
    """
    Add GET-parameters to URL. If parameters are exist then they will be changed.
        url - URL, string value
        params - dict {'GET-parameter name': 'value'}
    """
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urllib.urlencode(query)
    return urlparse.urlunparse(url_parts)


def add_response_headers(h):
    """
    Add HTTP-headers to response.
    Example:
        @add_response_headers({'Refresh': '10', 'X-Powered-By': 'Django'})
        def view(request):
            ....
    """
    def headers_wrapper(fun):
        def wrapped_function(*args, **kwargs):
            response = fun(*args, **kwargs)
            for k, v in h.iteritems():
                response[k] = v
            return response
        return wrapped_function
    return headers_wrapper


def full_url(path=None, secure=None):
    if secure is None:
        secure = u_settings.USE_HTTPS
    return '%s://%s%s' % ((secure and 'https' or 'http'), u_settings.SITE_DOMAIN, path or '')


def get_url_for_lang(request, lang):
    """
    Повертає посиланням на сторінку з request для мови lang.
    """
    assert lang in u_settings.LANGUAGES_CODES
    current_lang = translation.get_language()
    if lang != current_lang:
        r = request.resolver_match
        if r is None:
            r = resolve(request.path)
        translation.activate(lang)
        kwargs = r.kwargs.copy()
        kwargs['params_'] = request.GET
        url = resolve_url_ext(r.view_name, *r.args, **kwargs)
        translation.activate(current_lang)
    else:
        url = request.get_full_path()
    return url


def get_urls_for_langs(request):
    """
    Повертає словник з посиланням на дану сторінку для різних мов.
    {'en': '/about-us', 'uk': '/ua/pro-nas'}
    Повертає None, якщо в request немає resolver_match (тобто помилка на етапі process_request)
    Якщо в url використовується slug, тоді дана функція з цим не справиться.
    """
    urls = {}
    current_lang = translation.get_language()
    r = request.resolver_match
    if r is None:
        return None
    for lang in u_settings.LANGUAGES_CODES:
        if lang != current_lang:
            translation.activate(lang)
            kwargs = r.kwargs.copy()
            kwargs['params_'] = request.GET
            urls[lang] = resolve_url_ext(r.view_name, *r.args, **kwargs)
        else:
            urls[lang] = request.get_full_path()
    translation.activate(current_lang)
    return urls
