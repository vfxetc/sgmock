from common import *


class TestFixtures(TestCase):
    
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
        for name in ('Client', 'Online', 'Roto', 'MM', 'Anm', 'FX',
            'Light', 'Comp', 'Art', 'Model', 'Rig', 'Surface'
        ):
            self.assertIn(name, steps)
            self.assertEqual(name, steps[name]['name'])
            self.assertEqual(name, steps[name]['short_name'])
        
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