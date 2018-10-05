from common import *


class TestAssertion(TestCase):

    def test_assertSameEntity(self):
        pa = dict(type='Project', id=1, name='ProjectA')
        pb = dict(type='Project', id=2, name='ProjectB')
        sa = dict(type='Shot', id=1, name='ShotA')

        # Two entities with the same id's are found equal
        self.assertSameEntity(pa, dict(type='Project', id=1))

        # The two entities with the same id's but different types
        with self.assertRaises(AssertionError):
            self.assertSameEntity(pa, sa)

        # The two entities have the same type but different id's
        with self.assertRaises(AssertionError):
            self.assertSameEntity(pa, pb)

    def test_assertNotSameEntity(self):
        pa = dict(type='Project', id=1, name='ProjectA')
        pb = dict(type='Project', id=2, name='ProjectB')
        sa = dict(type='Shot', id=1, name='ShotA')

        self.assertNotSameEntity(pa, pb)
        # The two entities have the same type and id
        with self.assertRaises(AssertionError):
            self.assertNotSameEntity(pa, pa)
        with self.assertRaises(AssertionError):
            self.assertNotSameEntity(pa, dict(type='Project', id=1))

        # The two entities have different types but the same id's
        self.assertNotSameEntity(pa, sa)
