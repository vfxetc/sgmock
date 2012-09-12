from __future__ import absolute_import

from unittest import TestCase as BaseTestCase
import sys


class TestCase(BaseTestCase):
    
    def assertSameEntity(self, a, b, msg=None):
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
            self.fail(msg or '; '.join(errors))
            return
    
    def assertNotSameEntity(self, a, b, msg=None):
        errors = []
        
        for loc, x in (('1st', a), ('2nd', b)):
            if not isinstance(x, dict):
                errors.append('%s is a %r, not dict: %r' % (loc, type(x), x))
                continue
            if 'type' not in x:
                errors.append('%s has no type: %r' % (loc, x))
            if 'id' not in x:
                errors.append('%s has no id: %r' % (loc, x))
        
        if not errors and a['type'] == b['type'] and a['id'] == b['id']:
            errors.append('both entities are %s %s' % (a['type'], a['id']))
        
        if errors:
            self.fail(msg or '; '.join(errors))
            return
    
    # Add some of the unittest methods that we love from 2.7.
    if sys.version_info < (2, 7):
    
        def assertIs(self, a, b, msg=None):
            if a is not b:
                self.fail(msg or '%r at 0x%x is not %r at 0x%x; %r is not %r' % (type(a), id(a), type(b), id(b), a, b))
    
        def assertIsNot(self, a, b, msg=None):
            if a is b:
                self.fail(msg or 'both are %r at 0x%x; %r' % (type(a), id(a), a))
        
        def assertIsNone(self, x, msg=None):
            if x is not None:
                self.fail(msg or 'is not None; %r' % x)
        
        def assertIsNotNone(self, x, msg=None):
            if x is None:
                self.fail(msg or 'is None; %r' % x)
        
        def assertIn(self, a, b, msg=None):
            if a not in b:
                self.fail(msg or '%r not in %r' % (a, b))
        
        def assertNotIn(self, a, b, msg=None):
            if a in b:
                self.fail(msg or '%r in %r' % (a, b))
        
        def assertIsInstance(self, instance, types, msg=None):
            if not isinstance(instance, types):
                self.fail(msg or 'not an instance of %r; %r' % (types, instance))
        
        def assertNotIsInstance(self, instance, types, msg=None):
            if isinstance(instance, types):
                self.fail(msg or 'is an instance of %r; %r' % (types, instance))
