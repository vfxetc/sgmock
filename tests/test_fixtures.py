from common import *


class TestFixtures(TestCase):
    
    def test_proxy_commands(self):
        sg = Shotgun()
        fix = Fixture(sg)
        
        fix.create('Project', dict(name='this is the name'))
        self.assertEqual(len(fix.created), 1)
        self.assertEqual(sum(len(x) for x in sg._store.itervalues()), 1)
        
        fix.delete_all()
        self.assertEqual(len(fix.created), 0)
        self.assertEqual(sum(len(x) for x in sg._store.itervalues()), 0)
    
    def test_find_or_create(self):
        
        sg = Shotgun()
        fix = Fixture(sg)
        
        anim = fix.find_or_create('Step', short_code='Anim')
        self.assertEqual('Step', anim['type'])
        self.assertEqual(3, len(anim))
        self.assert_(anim['id'])
        self.assertEqual(anim['short_code'], 'Anim')
        
        anim2 = fix.find_or_create('Step', short_code='Anim')
        self.assertSameEntity(anim, anim2)
        self.assertIsNot(anim, anim2)
        
    def test_default_steps(self):
        
        sg = Shotgun()
        fix = Fixture(sg)
        
        self.assertEqual([], sg.find('Step', []))
        
        steps = fix.default_steps()
        
        # These are the default steps that we want to see.
        for code in ('Client', 'Online', 'Roto', 'MM', 'Anm', 'FX',
            'Light', 'Comp', 'Art', 'Model', 'Rig', 'Surface'
        ):
            self.assertIn(code, steps)
            self.assertEqual(code, steps[code]['code'])
            self.assertEqual(code, steps[code]['short_name'])
        
        anm = sg.find_one('Step', [('short_name', 'is', 'Anm')])
        self.assertSameEntity(steps['Anm'], anm)
        self.assertIsNot(steps['Anm'], anm)
    
    def test_shot_task_chain(self):
        
        sg = Shotgun()
        fix = Fixture(sg)
        
        proj = fix.Project(mini_uuid())
        print proj
        seq = proj.Sequence('AA')
        print seq
        shot = seq.Shot('AA_001')
        print shot
        step = fix.find_or_create('Step', short_code='Anim')
        print step
        task = shot.Task('Animate something', step=step)
        print task
        
        self.assertEqual(task['type'], 'Task')
        self.assertEqual(shot['type'], 'Shot')
        self.assertEqual(seq['type'], 'Sequence')
        self.assertEqual(proj['type'], 'Project')
        
        self.assertSameEntity(task['step'], step)
        self.assertSameEntity(task['entity'], shot)
        self.assertSameEntity(shot['sg_sequence'], seq)
        self.assertSameEntity(seq['project'], proj)
    
    
    def test_shot_task_chain_cleanup(self):
        sg = Shotgun()
        fix = Fixture(sg)
        
        proj = fix.Project(mini_uuid())
        seq = proj.Sequence('AA')
        shot = seq.Shot('AA_001')
        step = fix.find_or_create('Step', short_code='Anim')
        task = shot.Task('Animate something', step=step)
        
        self.assertEqual(len(fix.created), 5)
        self.assertEqual(sum(len(x) for x in sg._store.itervalues()), 5)
        
        fix.delete_all()
        self.assertEqual(len(fix.created), 0)
        self.assertEqual(sum(len(x) for x in sg._store.itervalues()), 0)
    