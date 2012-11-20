"""Mock replacement for ``shotgun_api3`` module."""

import collections
import copy
import datetime
import re
import itertools

import shotgun_api3


class ShotgunError(Exception):
    """Exception for all server logic."""
    pass

class Fault(ShotgunError):
    """Exception for all remote API logic; unused in this mock."""
    pass


_no_arg_sentinel = object()


class _IsFilter(object):
    
    def __init__(self, field, value):
        self.field = field
        self.value = value
    
    def __call__(self, entity_iter):
        for entity in entity_iter:
            if isinstance(self.value, dict):
                if (self.value.get('type') == entity.get(self.field, {}).get('type') and
                    self.value.get('id') == entity.get(self.field, {}).get('id')
                ):
                    yield entity
            elif entity.get(self.field) == self.value:
                yield entity


class _InFilter(object):
    
    def __init__(self, field, *values):
        self.field = field
        self.values = set(values)
    
    def __call__(self, entity_iter):
        for entity in entity_iter:
            if entity.get(self.field) in self.values:
                yield entity
                
class _LessThanFilter(object):
    
    def __init__(self, field, value):
        self.field = field
        self.value = value
    
    def __call__(self, entity_iter):
        for entity in entity_iter:
            if entity.get(self.field) < self.value:
                yield entity


_filters = {
    'is': _IsFilter,
    'in': _InFilter,
    'less_than': _LessThanFilter,
}


class _Config(object):
    pass

class Shotgun(object):
    
    """A mock Shotgun server, replicating the ``shotgun_api3`` interface.
    
    The constructor is a dummy and eats all arguments.
    
    """
    
    def __init__(self, base_url=None, *args, **kwargs):
        
        # Fake some attributes; effectively eat all the args.
        self.base_url = base_url or 'https://github.com/westernx/sgmock'
        self.server_url = self.base_url
        self.client_caps = None
        self.config = _Config()
        
        # Set everything else to be not implemented.
        def not_implemented(*args, **kwargs):
            raise NotImplementedError()
        for name in dir(shotgun_api3.Shotgun):
            if not hasattr(self, name):
                setattr(self, name, not_implemented)
        
        self._store = collections.defaultdict(dict)
        self._ids = collections.defaultdict(int)
        self._deleted = collections.defaultdict(dict)
        
    def connect(self):
        """Stub; does nothing."""
        pass
    
    def close(self):
        """Stub; does nothing."""
        pass
    
    def info(self):
        return {
            'version': '4.0.0',
        }
    
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
                minimal[field] = self._minimal_copy(self._resolve_link(v), ['name'])
            elif isinstance(v, list):
                res = []
                for x in v:
                    if isinstance(x, dict):
                        res.append(self._minimal_copy(x))
                    else:
                        res.append(x)
                minimal[field] = res
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
    
    # `entity.Shot.code.more` will return same as `entity.Shot.code`.
    _deep_lookup_re = re.compile(r'^(\w+)\.(\w+)\.([^.]+)')
    
    def _lookup_field(self, entity, field):
        
        # Simple fields.
        try:
            return entity[field]
        except KeyError:
            pass
        
        m = self._deep_lookup_re.match(field)
        if not m:
            
            parts = field.split('.')
            if any(not x for x in parts):
                raise ShotgunError('malformed field %r' % field)
            
            # Anything that looks kinda like a deep-link returns None.
            if len(parts) > 1:
                return None
                
            # Single fields are ignored.
            raise KeyError(field)
        
        local_field, link_type, deep_field = m.groups()
        # Get the link.
        try:
            link = entity[local_field]
        except KeyError:
            # Non existant local parts of a deep link are ignored.
            raise KeyError(field)

        # Non-entity deep-links are ignored.
        if not isinstance(link, dict):
            raise KeyError(field)
        
        # Deep-link type mismatches result in a None
        if not link['type'] == link_type:
            return None
        
        # Resolve the link, but let the error pop through since Shotgun would
        # never actually get to this state.
        linked = self._resolve_link(link)
        
        # There is only one level of a deep-link, and it always returns None.
        return linked.get(deep_field)
    
    def _reduce_links(self, data):
        if isinstance(data, dict):
            if 'type' in data and 'id' in data:
                if not self._entity_exists(data):
                    raise ShotgunError('linked entity %r does not exist' % self._minimal(data))
                return self._minimal_copy(data)
            res = {}
            for k, v in data.iteritems():
                res[k] = self._reduce_links(v)
            return res
        if isinstance(data, (list, tuple)):
            return list(self._reduce_links(x) for x in data)
        return data
    
    def _create_or_update(self, entity_type, entity_id, data, return_fields=None):
        
        # Get or create the entity.
        if entity_id is None:
            entity = {
                'type': entity_type,
                'id': self._ids[entity_type] + 1,
                'created_at': datetime.datetime.utcnow(),
            }
            self._ids[entity_type] = entity['id']
            self._store[entity_type][entity['id']] = entity
        else:
            # TODO: Handle this gracefully.
            entity = self._store[entity_type][entity_id]
         
        # Set some defaults.
        entity['updated_at'] = datetime.datetime.utcnow()
        
        # Reduce all links to the basic forms.
        data = dict(data)
        data.pop('id', None)
        entity.update(self._reduce_links(data))
        
        return entity
    
    def create(self, entity_type, data, return_fields=None):
        """Store an entity of the given type and data; return the new entity.
        
        :param str entity_type: The type of the entity.
        :param dict data: The fields for the new entity.
        :param list return_fields: Which fields to return from the server in
            addition to those explicitly stored; only good for ``updated_at``
            in this mock version.
        
        """
        entity = self._create_or_update(entity_type, None, data)
        return self._minimal_copy(entity, itertools.chain(data.iterkeys(), return_fields or ()))
        
    def update(self, entity_type, entity_id, data):
        
        # Perform the update.
        entity = self._create_or_update(entity_type, entity_id, data)
        
        # Return a copy with only the updated data in it.
        return dict((k, entity[k]) for k in set(itertools.chain(data, ('type', 'id'))))
        
    def find_one(self, entity_type, filters, fields=None, order=None, 
        filter_operator=None, retired_only=False):
        """Find and return a single entity.
        
        This is the same as calling :meth:`find` and only returning the first
        result.
        
        :return: ``dict`` or ``None``.
        
        """
        results = self.find(entity_type, filters, fields, order, 
            filter_operator, 1, retired_only)
        if results:
            return results[0]
        return None
    
    def find(self, entity_type, filters, fields=None, order=None, 
        filter_operator=None, limit=0, retired_only=False, page=0):
        """Find and return entities satifying a list of filters.
        
        We currently support deep-linked fields in the return fields, but not
        in filters.
        
        :param str entity_type: The type of entities to find.
        :param list filters: A list of `filters <https://github.com/shotgunsoftware/python-api/wiki/Reference%3A-Filter-Syntax>`_
        :param list fields: Which fields to return.
        :param order: Ignored.
        :param filter_operator: Ignored.
        :param limite: Ignored.
        :param retired_only: Ignored.
        :param page: Ignored.
        
        :return: ``list`` of ``dict``s.
        
        """
        # Wrap the base entities with all of the filters.
        entities = self._store[entity_type].itervalues()
        for filter_ in filters:
            filter_type = filter_[1]
            if filter_type not in _filters:
                raise ShotgunError('unknown filter %r' % filter_type)
            entities = _filters[filter_type](filter_[0], *filter_[2:])(entities)
        
        
        # Return minimal copies.
        res = [self._minimal_copy(entity, fields) for entity in entities]
        print '# sgmock.Shotgun.find(%r, %r) -> [%s]' % (entity_type, filters, ', '.join(str(e['id']) for e in res))
        return res
        
    _batch_type_args = {
        'create': ('entity_type', 'data'),
        'update': ('entity_type', 'entity_id', 'data'),
        'delete': ('entity_type', 'entity_id'),
    }
    
    def batch(self, requests):
        """Perform a series of requests in one request.
        
        This mock does not have transactions, so a failed request will leave
        the data store in a partially mutated state.
        
        :param list requests: A series of ``dicts`` representing requests.
        :return: ``list`` of results from calling methods individually.
        
        """
        
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
        
        # Error like Shotgun does, but perhaps with a slightly better message.
        if not responses:
            raise ShotgunError('batch must have at least one request')
        
        return responses
    
    def delete(self, entity_type, entity_id):
        """Delete a single entity.
        
        This mock does not have retired entities, so once it is deleted an
        entity is gone.
        
        :param str entity_type: The type of the entity to delete.
        :param int entity_id: The id of the entity to delete.
        :return bool: ``True`` if the entity did exist.
        
        """
        entity = self._store[entity_type].pop(entity_id, None)
        if entity:
            self._deleted[entity_type][entity_id] = entity
        return bool(entity)
    
    def revive(self, entity_type, entity_id):
        entity = self._deleted[entity_type].pop(entity_id, None)
        if entity:
            self._store[entity_type][entity_id] = entity
        return bool(entity)
        
    
    