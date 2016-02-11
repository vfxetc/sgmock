import json
import os
import logging
from datetime import datetime, date

from flask import Flask, request, Response, g

from .shotgun import Shotgun
from .exceptions import Fault, MockError


log = logging.getLogger('sgmock')


app = Flask('sgmock.server')


shotgun_by_namespace = {}

def get_namespace():
    return g.pragmas.get('sgmock_namespace')

def get_shotgun():
    namespace = get_namespace()
    try:
        return shotgun_by_namespace[namespace]
    except KeyError:
        return shotgun_by_namespace.setdefault(namespace, Shotgun())

def json_default(x):
    if isinstance(x, (datetime, date)):
        if isinstance(x, datetime):
            return x.strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            return x.strftime('%Y-%m-%d')
    else:
        return x

@app.route('/api3/json', methods=['POST'])
def json_api():

    payload = json.loads(request.data)
    if not isinstance(payload, dict):
        return '', 400, []

    g.pragmas = payload.get('pragmas') or {}
    g.shotgun = get_shotgun()
    #print json.dumps(payload, indent=4, sort_keys=True)

    try:
        method_name = payload['method_name']
        params = payload['params']
        auth_params = params[0] if params else {}
        method_params = params[1] if len(params) > 1 else {}
    except KeyError:
        return '', 400, []


    try:
        method = _api3_methods[method_name]
    except KeyError as e:
        result = {
            'exception': True,
            'error_code': 10000,
            'message': 'sgmock has no %s method' % method_name
        }
    else:
        try:
            result = method(method_params)
        except Fault as e:
            if isinstance(e, MockError):
                log.error(e.args[0])
            else:
                log.warning('Fault [%d]: %s' % (e.code, e.args[0]))
            result = {
                'exception': True,
                'error_code': e.code,
                'message': e.args[0],
            }

    if not (isinstance(result, (Response, basestring)) or (isinstance(result, (list, tuple)) and isinstance(result[0], (Response, basestring)))):
        result = json.dumps(result, default=json_default), 200, [('Content-Type', 'application/json')]

    return result



_api3_methods = {}

def api3_method(func):
    _api3_methods[func.__name__] = func
    return func


@api3_method
def info(params):
    return g.shotgun.info()


@api3_method
def read(params):
    type_ = params['type']
    filters = params['filters']
    fields = params['return_fields']
    page = params['paging']['current_page']
    limit = params['paging']['entities_per_page']
    entities = g.shotgun.find(type_, filters, fields, page=page, limit=limit)
    return {
        'entities': entities,
        'paging_info': {
            'entity_count': len(entities),
        },
    }


@api3_method
def create(params):
    type_ = params['type']
    data = dict((f['field_name'], f['value']) for f in params['fields'])
    return_fields = params['return_fields']
    entity = g.shotgun.create(type_, data, return_fields,
        _generate_events=g.pragmas.get('generate_events', True),
    )
    return {'results': entity}


@api3_method
def update(params):
    type_ = params['type']
    id_ = params['id']
    data = dict((f['field_name'], f['value']) for f in params['fields'])
    entity = g.shotgun.update(type_, id_, data)
    return {'results': entity}


@api3_method
def delete(params):
    type_ = params['type']
    id_ = params['id']
    res = g.shotgun.delete(type_, id_)
    return res


@api3_method
def clear(params):
    res = count(None)
    g.shotgun.clear()
    return res


@api3_method
def count(params):
    res = {}
    for type_, entities in g.shotgun._store.iteritems():
        if entities:
            res[type_] = len(entities)
    return res


def main():

    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 8020))

    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    log.info('Running on http://%s:%s/' % (host, port))

    app.run(host=host, port=port)


if __name__ == '__main__':
    main()
