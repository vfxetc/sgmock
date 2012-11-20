_required = object()


class Fixture(object):
    
    """Assistant for creating test fixtures.
    
    This proxies all undefined attributes to its :class:`~sgmock.shotgun.Shotgun`
    instance for easy tear-down of newly created entities. E.g::
    
        # Create a fixture wrapping a mock Shotgun.
        sg = Fixture(Shotgun())
        sg.create('Project', {'name': 'My Testing Project'})
        
        # Test some things.
        
        # Clean up everything we made.
        sg.delete_all()
    
    This also provides convenience methods to directly create entities with
    keyword arguments, and to create common entities with links
    to their parents/owners. e.g.::

        sg = Fixture(Shotgun())
        
        # Create a pipeline step.
        anim = sg.Step(code='Animation')
        
        # Create a project with a `name`.
        proj = sg.Project('My Testing Project')
        
        # Create a sequence with a `code`.
        seq = proj.Sequence('First Sequence')
        
        # Create a shot with a `code`.
        shot = seq.Shot('FS_001')
    
    The current understood heirarchy is::
    
        - Project
            - Asset
                - Task
            - Sequence
                - Shot
                    - Task
    
    """
    
    def __init__(self, shotgun):
        
        #: The :class:`~sgmock.shotgun.Shotgun` we will proxy and use for
        #: creation.
        self.shotgun = shotgun
        
        #: The ``list`` of created entities.
        self.created = []
    
    def __getattr__(self, name):
        if name[0].isupper():
            return _Creator(self, name)
        else:
            return getattr(self.shotgun, name)
            
    def create(self, *args, **kwargs):
        """Create an entity; proxies :meth:`~sgmock.shotgun.Shotgun.create`."""
        x = self.shotgun.create(*args, **kwargs)
        self.created.append((x['type'], x['id']))
        return x
        
    def delete_all(self):
        """Delete all entities that this fixture created or proxied the creation of."""
        if not self.created:
            return
        self.shotgun.batch([dict(
            request_type='delete',
            entity_type=type_,
            entity_id=id_,
        ) for type_, id_ in reversed(self.created)])
        self.created = []
        
    def find_or_create(self, entity_type, data=None, **kwargs):
        """Find an entity matching all of the given fields, or create it.
        
        :param str entity_type: The type of entity to find or create.
        :param dict data: The fields to look for or create.
        :return dict: The found or created entity.
        
        """
        
        if data and kwargs:
            raise ValueError('specify data or kwargs')
        data = data or kwargs
        
        filters = []
        for k, v in data.iteritems():
            filters.append((k, 'is', v))
        entity = self.shotgun.find_one(entity_type, filters, data.keys())
        if entity:
            return entity
        data = data.copy()
        data.pop('id', None)
        return self.create(entity_type, data, data.keys())
    
    def default_steps(self):
        """Return a dict mapping short_names to entities for a default set of steps.
        
        These steps are created if they don't exist, and include: ``Client``,
        ``Online``, ``Roto``, ``MM``, ``Anm``, ``FX``, ``Light``, ``Comp``,
        ``Art``, ``Model``, ``Rig``, and ``Surface``.
        
        """
        steps = {}
        for code in ('Client', 'Online', 'Roto', 'MM', 'Anm', 'FX',
            'Light', 'Comp', 'Art', 'Model', 'Rig', 'Surface'
        ):
            steps[code] = self.find_or_create('Step', dict(
                code=code,
                short_name=code))
        return steps


class _Creator(object):
    
    def __init__(self, fixture, entity_type, parent=None):
        self.fixture = fixture
        self.entity_type = entity_type
        self.parent = parent
        
    def __call__(self, *args, **kwargs):
        constructor = _entity_types.get(self.entity_type, _Entity)
        for name, default in constructor._argument_defaults:
            if name not in kwargs:
                if not args:
                    if default is _required:
                        raise TypeError('%s missing required %s' % (self.entity_type, name))
                    kwargs[name] = default
                else:
                    kwargs[name] = args[0]
                    args = args[1:]
        
        if self.parent:
            self.parent.prepare_child(self.entity_type, kwargs)
        raw = self.fixture.create(self.entity_type, kwargs, kwargs.keys())
        return constructor(self.fixture, self.parent, raw)


class _Entity(dict):
    
    _argument_defaults = []
    _parent = None
    _backrefs = {}
    
    def prepare_child(self, entity_type, kwargs):
        
        # Set backref to us.
        kwargs[self._backrefs[entity_type]] = self.minimal
            
        # Set the project.
        if self['type'] == 'Project':
            kwargs['project'] = self.minimal
        elif 'project' in self:
            kwargs['project'] = self['project'].copy()
        
    def __init__(self, fixture, parent, data):
        super(_Entity, self).__init__(data)
        self.fixture = fixture
    
    def __getattr__(self, name):
        if name[0].isupper() and name in self._backrefs:
            return _Creator(self.fixture, name, self)
        raise AttributeError(name)
    
    @property
    def minimal(self):
        return dict(type=self['type'], id=self['id'])


class _Project(_Entity):
    _argument_defaults = [('name', _required)]
    _backrefs = {
        'Sequence': 'project',
        'Asset': 'project',
    }

class _Sequence(_Entity):
    _argument_defaults = [('code', _required)]
    _parent = 'project'
    _backrefs = {'Shot': 'sg_sequence'}

class _Shot(_Entity):
    _argument_defaults = [('code', _required)]
    _parent = 'sg_sequence'
    _backrefs = {'Task': 'entity'}

class _Task(_Entity):
    _argument_defaults = [('content', _required)]
    _parent = 'entity'

class _Step(_Entity):
    _argument_defaults = [('short_name', _required)]

class _Asset(_Entity):
    _argument_defaults = [('code', _required), ('sg_asset_type', 'Generic')]
    _parent = 'project'
    _backrefs = {'Task': 'entity'}



_entity_types = dict(
    (name[1:], value)
    for name, value in globals().iteritems()
    if isinstance(value, type) and issubclass(value, _Entity)
)





