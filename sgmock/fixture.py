class Fixture(object):
    
    def __init__(self, shotgun):
        self.shotgun = shotgun
        self._pipeline_steps = {}
        
    def pipeline_steps(self):
        """Return a dict mapping short_names to entities for a default set of steps."""
        if not self._pipeline_steps:
            for short_name in ('Client', 'Online', 'Roto', 'MM', 'Anm', 'FX',
                'Light', 'Comp', 'Art', 'Model', 'Rig', 'Surface'
            ):
                self._pipeline_steps[short_name] = self.shotgun.create(
                    'Step', dict(short_name=short_name), ['short_name'])
        return self._pipeline_steps
        