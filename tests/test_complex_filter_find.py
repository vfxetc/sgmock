from common import *


class TestComplexFilterFind(TestCase):

    def test_basics(self, op_all='all', op_any='any'):

        sg = Shotgun()
        nameA = '{}_ProjectA'.format(mini_uuid())
        a = sg.create('Project', dict(name=nameA, sg_status='Bid'))
        nameB = '{}_ProjectB'.format(mini_uuid())
        b = sg.create('Project', dict(name=nameB, sg_status='Bid'))
        nameC = '{}_ProjectC'.format(mini_uuid())
        c = sg.create('Project', dict(name=nameC, sg_status='Production'))

        # Using AND as filter_operator
        query = [
            {
                'filter_operator': op_all,
                'filters': [
                    ['name', 'is', nameB],
                    ['sg_status', 'is', 'Bid'],
                ]
            }
        ]
        results = sg.find('Project', query)
        assert len(results) == 1
        self.assertSameEntity(results[0], b)

        # Using OR as filter_operator
        query = [
            {
                'filter_operator': op_any,
                'filters': [
                    ['name', 'is', nameB],
                    ['sg_status', 'is', 'Production'],
                ]
            }
        ]
        results = sg.find('Project', query)
        # NOTE: sgmock's find ignores order and always seems to return in index order
        self.assertSameEntity(results[0], a)
        self.assertSameEntity(results[1], c)

        # Combine an AND and OR query
        query = [
            ['sg_status', 'is', 'Bid'],
            {
                'filter_operator': op_any,
                'filters': [
                    ['name', 'is', nameA],
                    ['name', 'is', nameB],
                ]
            }
        ]
        results = sg.find('Project', query)
        assert len(results) == 2
        # NOTE: sgmock's find ignores order and always seems to return in index order
        self.assertSameEntity(results[0], a)
        self.assertSameEntity(results[1], b)

    def test_synonyms(self):
        # Assert the synonyms of the operators work too.
        self.test_basics('and', 'or')