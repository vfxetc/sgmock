import mock
import shotgun_api3


class ShotgunError(Exception):
    pass

class Fault(ShotgunError):
    pass


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
        
        self._store = {}
    
    def connect(self):
        pass
    
    def close(self):
        pass
    
    def _entity_exists(self, type_, id_):
        return type_ in self._store and id_ in self._store[type_]
    
    def create(self, entity_type, data, return_fields=None):
        
        # Reduce all links to the basic forms.
        to_store = {}
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
        
        self._store.setdefault(entity_type, []).append(to_store)
        to_store['id'] = len(self._store[entity_type])
        
        # Return only the fields we have been asked to return.
        ret = dict(type=entity_type, id=to_store['id'])
        for field in return_fields or []:
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
        pass
        
    def info(self):
        return {'version': [4, 0, 0]}
    
    