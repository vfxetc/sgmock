from __future__ import absolute_import

from unittest import TestCase as BaseTestCase


class TestCase(BaseTestCase):
    
    def assertIn(self, key, collection):
        if key not in collection:
            self.fail('%r not in %r' % (key, collection))
    
    def assertIsInstance(self, instance, types):
        if not isinstance(instance, types):
            self.fail('not an instance of %r; %r' % (types, instance))
    
    def assertIs(self, a, b):
        if a is not b:
            self.fail('%r at 0x%x is not %r at 0x%x; %r is not %r' % (type(a), id(a), type(b), id(b), a, b))
    
    def assertIsNot(self, a, b):
        if a is b:
            self.fail('both are %r at 0x%x; %r' % (type(a), id(a), a))
    
    def assertSameEntity(self, a, b):
        errors = []
        
        for loc, x in (('1st', a), ('2nd', b)):
            if not isinstance(x, dict):
                errors.append('%s is a %r, not dict: %r' % (loc, type(x), x))
                continue
            if 'type' not in x:
                errors.append('%s has no type: %r' % (loc, x))
            if 'id' not in x:
                errors.append('%s has no id: %r' % (loc, x))
        
        if not errors:
            if a['type'] != b['type']:
                errors.append('types do not match; %r != %r' % (a['type'], b['type']))
                if a['id'] != b['id']:
                    errors.append('ids do not match; %r != %r' % (a['id'], b['id']))
        
        if errors:
            self.fail('; '.join(errors))
            return
