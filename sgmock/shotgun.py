import collections
import copy
import re

import mock
import shotgun_api3


class ShotgunError(Exception):
    pass

class Fault(ShotgunError):
    pass


_no_arg_sentinel = object()


class _IsFilter(object):
    
    def __init__(self, field, value):
        self.field = field
        self.value = value
    
    def __call__(self, entity_iter):
        for entity in entity_iter:
            if entity.get(self.field) == self.value:
                yield entity


_filters = {
    'is': _IsFilter
}


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

    def info(self):
        return {'version': [4, 0, 0]}
    
    def _entity_exists(self, entity):
        """Return True if the referenced entity does exist in our store."""
        try:
            return entity['id'] in self._store[entity['type']]
        except KeyError:
            raise ShotgunError('entity does not have type and id; %r' % entity)
    
    def _minimal_copy(self, entity, fields=None):
        """Get a minimal representation of the given entity; only type and id."""
        try:
            minimal = dict(type=str(entity['type']), id=int(entity['id']))
        except KeyError:
            raise ShotgunError('entity does not have type and id; %r' % entity)
        for field in fields or ():
            try:
                v = self._lookup_field(entity, field)
            except KeyError:
                continue
            if isinstance(v, dict):
                minimal[field] = self._minimal_copy(v)
            else:
                minimal[field] = v
        return minimal
    
    def _resolve_link(self, link):
        """Convert a link to a full entity."""
        try:
            type_ = link['type']
            id_ = link['id']
        except KeyError:
            raise ShotgunError('entity does not have type and id; %r' % link)
        try:
            return self._store[type_][id_]
        except KeyError:
            raise ShotgunError('linked entity does not exist; %r' % link)
    
    _deep_lookup_re = re.compile(r'^(\w+)\.(\w+)\.([\w.]+)$')
    
    def _lookup_field(self, entity, field, default=_no_arg_sentinel):
        
        try:
            return entity[field]
        except KeyError:
            pass
        
        m = self._deep_lookup_re.match(field)
        if not m:
            raise KeyError(field)
        
        local_field, link_type, deep_field = m.groups()
            
        # Get the link.
        try:
            link = entity[local_field]
        except KeyError:
            if default is _no_arg_sentinel:
                raise ShotgunError('entity has no field %r; %r' % (local_field, entity))
            return default
            
        if not isinstance(link, dict):
            raise ShotgunError('non-entity value for deep linking at %r; %r' % (local_field, entity))
        if not link['type'] == link_type:
            raise ShotgunError('deep-link type mismatch; %r is not %r' % (link, link_type))
            
        # Go to the next step in the link.
        linked = self._resolve_link(link)
        return self._lookup_field(linked, deep_field, default)
            
    def create(self, entity_type, data, return_fields=None):
        """Create an entity of the given type and data; return the new entity."""
        
        # Reduce all links to the basic forms.
        to_store = {'type': entity_type}
        for k, v in data.iteritems():
            if isinstance(v, dict):
                # Make sure the link exists.
                if not self._entity_exists(v):
                    raise ShotgunError('linked entity %r does not exist' % self._minimal(v))
                to_store[k] = self._minimal_copy(v)
            else:
                to_store[k] = v
        
        # Store it.
        to_store['id'] = len(self._store[entity_type]) + 1
        self._store[entity_type][to_store['id']] = to_store
        
        # Return only the fields we have been asked to return.
        return self._minimal_copy(to_store, return_fields)
    
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
        
        # Return minimal copies.
        return [self._minimal_copy(entity, fields) for entity in entities]
        
    _batch_type_args = {
        'create': ('entity_type', 'data'),
        'update': ('entity_type', 'entity_id', 'data'),
        'delete': ('entity_type', 'entity_id'),
    }
    
    def batch(self, requests):
        responses = []
        
        for request in requests:
            
            try:
                type_ = request['request_type']
            except KeyError:
                raise ShotgunError('missing request_type; %r' % request)
            
            try:
                arg_names = self._batch_type_args[type_]
            except KeyError:
                raise ShotgunError('unknown request_type %r; %r' % (type_, request))
            
            try:
                args = tuple(request[name] for name in arg_names)
            except KeyError, e:
                raise ShotgunError('%s request missing %s; %r' % (type_, e.args[0], request))
            
            responses.append(getattr(self, type_)(*args))
        
        return responses
    
    