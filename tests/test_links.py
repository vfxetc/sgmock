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
        self.assertEqual(3, len(found_seq['project']))
        self.assertIn('name', found_seq['project'])
        
        found_seq2 = sg.find('Sequence', [], ['project'])[0]
        self.assertSameEntity(seq, found_seq2)
        self.assertIsNot(found_seq, found_seq2)
        self.assertSameEntity(proj, found_seq2.get('project'))
        self.assertIsNot(proj, found_seq2.get('project'))
        self.assertIsNot(found_seq.get('project'), found_seq2.get('project'))
        
    def test_scalar_deep_link(self):
        sg = Shotgun()
        name = mini_uuid()
        proj = sg.create('Project', dict(name=name))
        seq = sg.create('Sequence', dict(code='AA', project=proj))
        found_seq = sg.find('Sequence', [], ['project.Project.name'])[0]
        self.assertSameEntity(seq, found_seq)
        self.assertEqual(3, len(found_seq))
        self.assertEqual(name, found_seq['project.Project.name'])
    
    def test_missing_deep_links(self):
        
        sg = Shotgun()
        proj = sg.create('Project', dict(name='whatever'))
        seq = sg.create('Sequence', dict(code='AA', project=proj))
        shot = sg.create('Shot', dict(code='AA_001', sg_sequence=seq, project=proj))
        step = sg.create('Step', dict(code="Anim", short_name="Anim"))
        task = sg.create('Task', dict(entity=shot, step=step, content="Animate Something"))
        
        # There are a lot of wierd results with deep links in Shotgun 4.0.0...
        
        result = sg.find_one('Task', [], [
            'entity',
            'entity.Sequence',
            'entity.Shot',
            'entity.Shot.code',
            'entity.Shot.code.more',
            'entity.Shot.does_not_exist',
            'entity.Asset.code',
            'entity.Asset.code.more',
            'entity.Asset.sg_asset_type',
            'entity.Shot.sg_sequence',
            'entity.Shot.sg_sequence.Sequence.code',
        ])
        
        self.assertSameEntity(result['entity'], shot)
        for name in 'entity.Sequence', 'entity.Shot', 'entity.Shot.does_not_exist', 'entity.Asset.code', 'entity.Asset.code.more', 'entity.Asset.sg_asset_type':
            self.assertIn(name, result)
            self.assertIsNone(result[name])
        self.assertEqual(result['entity.Shot.code'], shot['code'])
        self.assertEqual(result['entity.Shot.code.more'], shot['code'])
        self.assertSameEntity(result['entity.Shot.sg_sequence'], seq)
        self.assertSameEntity(result['entity.Shot.sg_sequence.Sequence.code'], seq)
        
        
