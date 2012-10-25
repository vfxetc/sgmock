from common import *


class TestLists(TestCase):
    
    def test_lists_are_copied(self):
        
        sg = Shotgun()
        
        strings = ['a', 'b', 'c']
        a = sg.create('Dummy', {'strings': strings})
        b = sg.find_one('Dummy', [('id', 'is', a['id'])], ['strings'])
        c = sg.find_one('Dummy', [('id', 'is', a['id'])], ['strings'])
        
        
        self.assertSameEntity(a, b)
        self.assertSameEntity(a, c)
        
        self.assertEqual(strings, b['strings'])
        self.assertEqual(b['strings'], c['strings'])
        
        self.assertIsNot(strings, b['strings'])
        self.assertIsNot(b['strings'], c['strings'])
        
        
    def test_lists_are_collapsed(self):
        
        sg = Shotgun()
        
        fruits = []
        for name in ('apple', 'banana', 'strawberry'):
            fruits.append(sg.create('Fruit', {'name': name}))
        
        a = sg.create('Bowl', {'fruits': fruits})
        b = sg.find_one('Bowl', [('id', 'is', a['id'])], ['fruits'])
        c = sg.find_one('Bowl', [('id', 'is', a['id'])], ['fruits'])
        
        self.assertSameEntity(a, b)
        self.assertSameEntity(a, c)
        
        self.assertEqual(len(fruits), len(b['fruits']))
        self.assertEqual(len(fruits), len(c['fruits']))
        for x, y, z in zip(fruits, b['fruits'], c['fruits']):
            self.assertSameEntity(x, y)
            self.assertSameEntity(x, z)
            self.assertIsNot(x, y)
            self.assertIsNot(x, z)
            self.assertIsNot(y, z)
    
    