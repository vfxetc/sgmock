from common import *


class TestNonData(TestCase):
    
    def test_connect_and_close(self):
        sg = Shotgun()
        sg.connect()
        sg.close()


class TestSimpleCreate(TestCase):
    
    def test_create_default_return(self):
        sg = Shotgun()
        type_ = 'Dummy' + mini_uuid().upper()
        spec = dict(name=mini_uuid())
        proj = sg.create(type_, spec)
        self.assertIsNot(spec, proj)
        self.assertEqual(len(proj), 2)
        self.assertEqual(proj['type'], type_)
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


class TestSimpleFind(TestCase):
    
    def test_create_and_find_only_one_by_name(self):
        sg = Shotgun()
        name = mini_uuid()
        a = sg.create('Project', dict(name=name))
        b = sg.find('Project', [('name', 'is', name)])[0]
        self.assertSameEntity(a, b)


class TestLinkedCreate(TestCase):
    
    def test_create_sequence(self):
        sg = Shotgun()
        proj = sg.create('Project', dict(name=mini_uuid()))
        seq = sg.create('Sequence', dict(code='AA', project=proj))
        
        found_proj = sg.find('Project', [])[0]
        self.assertSameEntity(proj, found_proj)
        self.assertIsNot(proj, found_proj)
        self.assertEqual(2, len(found_proj))
        
        found_seq = sg.find('Sequence', [])[0]
        self.assertSameEntity(seq, found_seq)
        self.assertIsNot(seq, found_seq)
        self.assertEqual(2, len(found_seq))
        
        found_seq = sg.find('Sequence', [], ['project'])[0]
        self.assertSameEntity(seq, found_seq)
        self.assertSameEntity(proj, found_seq.get('project'))
        self.assertIsNot(proj, found_seq.get('project'))
        self.assertEqual(3, len(found_seq))
        self.assertEqual(2, len(found_seq['project']))
        
        