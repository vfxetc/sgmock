from common import *


class TestNonData(TestCase):
    
    def test_connect_and_close(self):
        sg = Shotgun()
        sg.connect()
        sg.close()


class TestSimpleData(TestCase):
    
    def test_create_default_return(self):
        sg = Shotgun()
        proj = sg.create('Project', dict(name=mini_uuid()))
        self.assertEqual(len(proj), 2)
        self.assertEqual(proj['type'], 'Project')
        self.assert_(proj['id'])
    
    def test_create_additional_return(self):
        sg = Shotgun()
        name = mini_uuid()
        proj = sg.create('Project', dict(name=name), ['name'])
        self.assertEqual(len(proj), 3)
        self.assertEqual(proj['type'], 'Project')
        self.assert_(proj['id'])
        self.assertEqual(proj['name'], name)
    
    def test_create_missing_return(self):
        sg = Shotgun()
        name = mini_uuid()
        proj = sg.create('Project', dict(name=name), ['name', 'does_not_exist'])
        self.assertEqual(len(proj), 3)
        self.assertEqual(proj['type'], 'Project')
        self.assert_(proj['id'])
        self.assertEqual(proj['name'], name)
    
    def test_create_and_find_first_by_id(self):
        sg = Shotgun()
        name = mini_uuid()
        a = sg.create('Project', dict(name=name))
        b = sg.find('Project', [('name', 'is', name)])[0]
        self.assertSameEntity(a, b)