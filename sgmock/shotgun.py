import collections
import copy

import mock
import shotgun_api3


class ShotgunError(Exception):
    pass

class Fault(ShotgunError):
    pass


_filters = {}
def _register_filter(operator):
    def _as_filter(func):
        _filters[operator] = func
        return func
    return _as_filter


@_register_filter('is')
class _IsFilter(object):
    
    def __init__(self, field, value):
        self.field = field
        self.value = value
    
    def __call__(self, entity_iter):
        for entity in entity_iter:
            if entity.get(self.field) == self.value:
                yield entity


class Shotgun(object):
    
    def __init__(self, base_url=None, *args, **kwargs):
        
        # Fake some attributes; effectively eat all the args.
        self.base_url = base_url or 'https://github.com/westernx/sgmock'
        self.client_caps = mock.Mock(shotgun_api3.shotgun.ServerCapabilities, side_effect=NotImplementedError)
        self.config = mock.Mock(shotgun_api3.shotgun._Config, side_effect=NotImplementedError)
        
        # Set everything else to be not implemented.
        def not_implemented(*args, **kwargs):
            raise NotImplementedError()
        for name in dir(shotgun_api3.Shotgun):
            if not hasattr(self, name):
                setattr(self, name, not_implemented)
        
        self._store = collections.defaultdict(dict)
    
    def connect(self):
        pass
    
    def close(self):
        pass
    
    def _entity_exists(self, type_, id_):
        return type_ in self._store and id_ in self._store[type_]
    
    def create(self, entity_type, data, return_fields=None):
        
        # Reduce all links to the basic forms.
        to_store = {'type': entity_type}
        for k, v in data.iteritems():
            if isinstance(v, dict):
                try:
                    type_ = str(v['type'])
                    id_ = int(v['id'])
                except KeyError:
                    raise ShotgunError('linked entity must have type and id')
                else:
                    # Make sure the link exists.
                    if not self._entity_exists(type_, id_):
                        raise ShotgunError('linked entity %s:%d does not exist' % (type_, id_))
                    to_store[k] = dict(type=type_, id=id_)
            else:
                to_store[k] = v
        
        to_store['id'] = len(self._store[entity_type]) + 1
        self._store[entity_type][to_store['id']] = to_store
        
        # Return only the fields we have been asked to return.
        ret = dict(type=entity_type, id=to_store['id'])
        for field in return_fields or ():
            if field in to_store:
                ret[field] = to_store[field]
        return ret
    
    def find_one(self, entity_type, filters, fields=None, order=None, 
        filter_operator=None, retired_only=False):

        results = self.find(entity_type, filters, fields, order, 
            filter_operator, 1, retired_only)
        if results:
            return results[0]
        return None
    
    def find(self, entity_type, filters, fields=None, order=None, 
        filter_operator=None, limit=0, retired_only=False, page=0):
        
        # Wrap the base entities with all of the filters.
        entities = self._store[entity_type].itervalues()
        for filter_ in filters:
            filter_type = filter_[1]
            if filter_type not in _filters:
                raise ShotgunError('unknown filter %r' % filter_type)
            entities = _filters[filter_type](filter_[0], *filter_[2:])(entities)
        
        ret = []
        for entity in entities:
            selected = dict(type=entity['type'], id=entity['id'])
            for field in fields or ():
                try:
                    v = entity[field]
                except KeyError:
                    pass
                else:
                    if isinstance(v, dict):
                        selected[field] = dict(type=v['type'], id=v['id'])
                    else:
                        selected[field] = v
            ret.append(selected)
        return ret
        
        
    def info(self):
        return {'version': [4, 0, 0]}
    
    