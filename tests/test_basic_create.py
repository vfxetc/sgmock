from common import *


class TestBasicCreate(TestCase):
    
    def test_create_default_return(self):
        sg = Shotgun()
        type_ = 'Dummy' + mini_uuid().upper()
        spec = dict(name=mini_uuid())
        proj = sg.create(type_, spec)
        print proj
        self.assertIsNot(spec, proj)
        self.assertEqual(len(proj), 3)
        self.assertEqual(proj['type'], type_)
        self.assertEqual(proj['name'], spec['name'])
        self.assert_(proj['id'])
    
    def test_create_additional_return(self):
        sg = Shotgun()
        type_ = 'Dummy' + mini_uuid().upper()
        name = mini_uuid()
        proj = sg.create(type_, dict(name=name), ['name'])
        self.assertEqual(len(proj), 3)
        self.assertEqual(proj['type'], type_)
        self.assert_(proj['id'])
        self.assertEqual(proj['name'], name)
    
    def test_create_missing_return(self):
        sg = Shotgun()
        type_ = 'Dummy' + mini_uuid().upper()
        name = mini_uuid()
        proj = sg.create(type_, dict(name=name), ['name', 'does_not_exist'])
        self.assertEqual(len(proj), 3)
        self.assertEqual(proj['type'], type_)
        self.assert_(proj['id'])
        self.assertEqual(proj['name'], name)
