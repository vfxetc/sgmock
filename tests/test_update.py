from common import *


class TestDelete(TestCase):
    
    def test_basic_update(self):
        
        sg = Shotgun()
        
        a = sg.create('Dummy', {})
        b = sg.update('Dummy', a['id'], {'key': 'value'})
        
        self.assertSameEntity(a, b)
        self.assertEqual(b.get('key'), 'value')
        self.assertIsNot(a, b)
        self.assertNotEqual(a, b)
        