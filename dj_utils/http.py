import simplejson
from django.http import HttpResponse


def send_json(data, content_type='application/json', status=200, json_dumps_kwargs=None):
    if json_dumps_kwargs is None:
        json_dumps_kwargs = {}
    return HttpResponse(
        simplejson.dumps(data, **json_dumps_kwargs),
        content_type=content_type,
        status=status
    )
