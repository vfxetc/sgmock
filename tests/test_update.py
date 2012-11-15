from common import *


class TestUpdate(TestCase):
    
    def test_basic_update(self):
        
        sg = Shotgun()
        
        a = sg.create('Dummy', {})
        b = sg.update('Dummy', a['id'], {'key': 'value'})
        
        self.assertSameEntity(a, b)
        self.assertEqual(b.get('key'), 'value')
        self.assertIsNot(a, b)
        self.assertNotEqual(a, b)
    
    def test_limited_fields(self):
        
        sg = Shotgun()
        a = sg.create('Dummy', {})
        b = sg.update('Dummy', a['id'], {'key': 'value'})
        c = sg.update('Dummy', a['id'], {'key2': 'value2'})
        
        self.assertEqual(set(b), set(('type', 'id', 'key')))
        self.assertEqual(set(c), set(('type', 'id', 'key2')))
        
        