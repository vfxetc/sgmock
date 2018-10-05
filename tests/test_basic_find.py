from common import *


class TestBasicFind(TestCase):

    def createTwoProjects(self, sg):
        nameA = 'A_Project_{}_ProjectA'.format(mini_uuid())
        a = sg.create('Project', dict(name=nameA))
        nameB = 'B_Project_{}_ProjectB'.format(mini_uuid())
        b = sg.create('Project', dict(name=nameB))
        return nameA, a, nameB, b

    def test_create_and_find_only_one_by_name(self):
        sg = Shotgun()
        name = mini_uuid()
        a = sg.create('Project', dict(name=name))
        b = sg.find('Project', [('name', 'is', name)])[0]
        self.assertSameEntity(a, b)
        b = sg.find('Project', [('id', 'is', a['id'])])[0]
        self.assertSameEntity(a, b)

    def test_create_is_not(self):
        sg = Shotgun()
        nameA, a, nameB, b = self.createTwoProjects(sg)
        c = sg.find('Project', [['name', 'is_not', nameA]])
        self.assertEqual(len(c), 1)
        self.assertSameEntity(b, c[0])
        c = sg.find('Project', [['name', 'is_not', nameB]])
        self.assertEqual(len(c), 1)
        self.assertSameEntity(a, c[0])

        c = sg.find('Project', [('id', 'is_not', a['id'])])
        self.assertEqual(len(c), 1)
        self.assertSameEntity(b, c[0])

    def test_less_than(self):
        sg = Shotgun()
        nameA, a, nameB, b = self.createTwoProjects(sg)
        c = sg.find('Project', [['id', 'less_than', 2]])
        self.assertEqual(len(c), 1)
        self.assertSameEntity(a, c[0])

        c = sg.find('Project', [['id', 'less_than', 3]])
        self.assertEqual(len(c), 2)
        self.assertSameEntity(a, c[0])
        self.assertSameEntity(b, c[1])

    def test_greater_than(self):
        sg = Shotgun()
        nameA, a, nameB, b = self.createTwoProjects(sg)
        c = sg.find('Project', [['id', 'greater_than', 1]])
        self.assertEqual(len(c), 1)
        self.assertSameEntity(b, c[0])

        c = sg.find('Project', [['id', 'greater_than', 0]])
        self.assertEqual(len(c), 2)
        self.assertSameEntity(a, c[0])
        self.assertSameEntity(b, c[1])

    def test_starts_with(self):
        sg = Shotgun()
        nameA, a, nameB, b = self.createTwoProjects(sg)
        filters = [['name', 'starts_with', 'B_Project_']]
        c = sg.find('Project', filters, ['name'])
        self.assertEqual(len(c), 1)
        self.assertSameEntity(b, c[0])
        self.assertEqual(c[0]['name'], nameB)

    def test_ends_with(self):
        sg = Shotgun()
        nameA, a, nameB, b = self.createTwoProjects(sg)
        filters = [['name', 'ends_with', '_ProjectB']]
        c = sg.find('Project', filters, ['name'])
        self.assertEqual(len(c), 1)
        self.assertSameEntity(b, c[0])
        self.assertEqual(c[0]['name'], nameB)
