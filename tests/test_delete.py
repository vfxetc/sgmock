from common import *


class TestDelete(TestCase):
    
    def test_id_reuse(self):
        sg = Shotgun()
        
        a = sg.create('Dummy', {})
        sg.delete('Dummy', a['id'])
        self.assertIsNone(sg.find_one('Dummy', [('id', 'is', a['id'])]))
        
        b = sg.create('Dummy', {})
        self.assertNotSameEntity(a, b, 'Deleted ID was reused')
    
    def test_revive(self):
        
        sg = Shotgun()
        a = sg.create('Dummy', {})
        sg.delete('Dummy', a['id'])
        self.assertIsNone(sg.find_one('Dummy', [('id', 'is', a['id'])]))
        
        sg.revive('Dummy', a['id'])
        self.assertSameEntity(a, sg.find_one('Dummy', [('id', 'is', a['id'])]))
    