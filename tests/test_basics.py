from common import *


class TestNonData(TestCase):
    
    def test_connect_and_close(self):
        sg = Shotgun()
        sg.connect()
        sg.close()


class TestSimpleData(TestCase):
    
    def test_create_one(self):
        sg = Shotgun()
        proj = sg.create('Project', dict(name=mini_uuid()))
        self.assertEqual(proj['type'], 'Project')
        self.assert_(proj.get('id'))
        
    def test_create_and_find_by_id(self):
        sg = Shotgun()
        name = mini_uuid()
        a = sg.create('Project', dict(name=name))
        b = sg.find('Project', [('name', 'is', name)])
        self.assertSameEntity(a, b)