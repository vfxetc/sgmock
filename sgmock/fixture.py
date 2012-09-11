_required = object()


class _Creator(object):
    
    _argument_defaults = {
        'Step': [('short_name', _required)],
        'Sequence': [('code', _required)],
        'Shot': [('code', _required)],
    }
    
    def __init__(self, fixture, entity_type):
        self.fixture = fixture
        self.entity_type = entity_type
    
    def __call__(self, *args, **kwargs):
        specs = self._argument_defaults.get(self.entity_type, ())
        for name, default in specs:
            if name not in kwargs:
                if not args:
                    if default is _required:
                        raise TypeError('%s missing required %s' % (self.entity_type, name))
                    kwargs[name] = default
                else:
                    kwargs[name] = args[0]
                    args = args[1:]
        return self.fixture.shotgun.create(self.entity_type, kwargs, kwargs.keys())


class Fixture(object):
    
    def __init__(self, shotgun):
        self.shotgun = shotgun
    
    def __getattr__(self, name):
        if name[0].isupper():
            return _Creator(self, name)
        else:
            raise AttributeError(name)
    
    def find_or_create(self, entity_type, datum=None, **kwargs):
        
        if datum and kwargs:
            raise ValueError('specify datum or kwargs')
        if kwargs:
            datum = [kwargs]
            is_single = True
        elif isinstance(datum, dict):
            datum = [datum]
            is_single = True
        else:
            is_single = False
        
        result = []
        for data in datum:
            filters = []
            for k, v in data.iteritems():
                filters.append((k, 'is', v))
            entity = self.shotgun.find_one(entity_type, filters, data.keys())
            if entity:
                result.append(entity)
                continue
            data = data.copy()
            data.pop('id', None)
            result.append(self.shotgun.create(entity_type, data, data.keys()))
        
        return result[0] if is_single else result
    
    def default_steps(self):
        """Return a dict mapping short_names to entities for a default set of steps."""
        steps = {}
        for short_name in ('Client', 'Online', 'Roto', 'MM', 'Anm', 'FX',
            'Light', 'Comp', 'Art', 'Model', 'Rig', 'Surface'
        ):
            steps[short_name] = self.find_or_create('Step', dict(short_name=short_name))
        return steps