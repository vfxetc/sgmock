from common import *


class TestLinks(TestCase):
    
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
        
