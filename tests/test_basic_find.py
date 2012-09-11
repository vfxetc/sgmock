from common import *


class TestBasicFind(TestCase):
    
    def test_create_and_find_only_one_by_name(self):
        sg = Shotgun()
        name = mini_uuid()
        a = sg.create('Project', dict(name=name))
        b = sg.find('Project', [('name', 'is', name)])[0]
        self.assertSameEntity(a, b)
