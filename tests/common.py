from pprint import pprint
from unittest import TestCase as BaseTestCase
import os

import shotgun_api3

from sgmock import Shotgun


def mini_uuid():
    return os.urandom(4).encode('hex')


class TestCase(BaseTestCase):
    
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
