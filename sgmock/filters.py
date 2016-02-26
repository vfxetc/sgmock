from datetime import datetime

from .exceptions import Fault, MockError

_filters = {}


def match_types(a, b):
    if isinstance(a, datetime) and isinstance(b, basestring):
        return (a.strftime('%Y-%m-%dT%H:%M:%SZ'), b)
    if isinstance(a, basestring) and isinstance(b, datetime):
        return (a, b.strftime('%Y-%m-%dT%H:%M:%SZ'))
    else:
        return a, b


def And(filters):
    def _And(entity):
        return all(f(entity) for f in filters)
    return _And

def Or(filters):
    def _Or(entity):
        return any(f(entity) for f in filters)
    return _Or



def _compile_filters(filters):

    if isinstance(filters, dict):
        op = filters.get('logical_operator', 'and')
        conditions = filters['conditions']
    else:
        op = 'and'
        conditions = filters

    op_cls = Or if op == 'or' else And
    return op_cls([_compile_condition(f) for f in conditions])


def _compile_condition(condition):

    if isinstance(condition, dict):
        if 'logical_operator' in condition:
            return _compile_filters(condition)

        op_name = condition['relation']
        field = condition['path']
        values = condition['values']

    elif len(condition) == 3 and isinstance(condition[2], (list, tuple)):
        field, op_name, values = condition
    else:
        field = condition[0]
        op_name = condition[1]
        values = condition[2:]

    op_cls = _filters.get(op_name)
    if not op_cls:
        raise MockError('unknown filter relation %r' % op_name)
    return op_cls(field, *values)


def filter_entities(filters, entities):
    compiled = _compile_filters(filters)
    return (e for e in entities if compiled(e))



def NotWrap(cls):
    class _Not(object):
        def __init__(self, *args):
            self.filter = cls(*args)
        def __call__(self, entity):
            return not self.filter(entity)
    return _Not


def register(*names, **kwargs):
    wrap = kwargs.pop('wrap', None)
    def _register(cls):
        for name in names:
            _filters[name] = wrap(cls) if wrap else cls
        return cls
    return _register


class ScalarFilter(object):

    def __init__(self, field, value):
        self.field = field
        self.value = value

    def __call__(self, entity):
        value, other = match_types(self.value, entity.get(self.field))
        return self.test(value, other)

    def test(self, value, field):
        raise NotImplementedError()


@register('is')
@register('is_not', wrap=NotWrap)
class IsFilter(ScalarFilter):

    def test(self, value, field):
        if isinstance(value, dict):
            return (
                value.get('type') == (field or {}).get('type') and
                value.get('id') == (field or {}).get('id')
            )
        else:
            return value == field


@register('in')
@register('not_in', wrap=NotWrap)
class InFilter(object):

    def __init__(self, field, *values):
        self.field = field
        self.values = set(values)

    def __call__(self, entity):
        return entity.get(self.field) in self.values


@register('less_than')
class LessThanFilter(ScalarFilter):
    def test(self, value, field):
        return field < value

@register('greater_than')
class LessThanFilter(ScalarFilter):
    def test(self, value, field):
        return field > value


@register('starts_with')
class StartsWithFilter(ScalarFilter):

    def test(self, value, field):
        return field.startswith(value)
