from common import *


class TestFixtures(TestCase):
    
    def test_default_pipeline(self):
        
        sg = Shotgun()
        fix = Fixture(sg)
        
        self.assertEqual([], sg.find('Step', []))
        
        steps = fix.pipeline_steps()
        
        # These are the default steps that we want to see.
        self.assertIn('Anm', steps)
        self.assertIn('Art', steps)
        self.assertIn('Client', steps)
        self.assertIn('Comp', steps)
        self.assertIn('FX', steps)
        self.assertIn('Light', steps)
        self.assertIn('MM', steps)
        self.assertIn('Model', steps)
        self.assertIn('Online', steps)
        self.assertIn('Rig', steps)
        self.assertIn('Roto', steps)
        self.assertIn('Surface', steps)
        
        anm = sg.find_one('Step', [('short_name', 'is', 'Anm')])
        self.assertSameEntity(steps['Anm'], anm)
        self.assertIsNot(steps['Anm'], anm)
        
