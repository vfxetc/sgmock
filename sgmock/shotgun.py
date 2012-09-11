import collections
import copy

import mock
import shotgun_api3


class ShotgunError(Exception):
    pass

class Fault(ShotgunError):
    pass


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
                minimal[field] = entity[field]
            except KeyError:
                pass
        return minimal
    
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
        
        to_return = []
        for entity in entities:
            restricted = dict(type=entity['type'], id=entity['id'])
            for field in fields or ():
                
                # If the requested field doesn't exist, just skip it.
                try:
                    v = entity[field]
                except KeyError:
                    continue
                    
                # We don't want to return our link, but a copy of it.
                if isinstance(v, dict):
                    restricted[field] = v.copy()
                else:
                    restricted[field] = v
            
            to_return.append(restricted)
        return to_return
        
        
    def info(self):
        return {'version': [4, 0, 0]}
    
    