import random

from .base import Fixture


# From various online generators.
project_names = [
    'Waiting for Johnson',
    'Helping Delilah',
    'Finding Gump',
    'Double Danger',
    'Master of Surrender',
    'Compulsive Winter',
    'Inner Space',
]

# All of the WesternX sequence codes from previous films.
sequence_names = [
    'AB', 'BA', 'BB', 'BD', 'BE', 'BL', 'BS', 'BU', 'BX', 'CD', 'CF', 'CT',
    'DB', 'DC', 'DD', 'DR', 'ED', 'FX', 'GB', 'GC', 'GP', 'GR', 'HH', 'HT',
    'IC', 'IP', 'JK', 'JS', 'LP', 'MB', 'MD', 'MP', 'MS', 'NP', 'NS', 'OS',
    'PB', 'PJ', 'PM', 'PR', 'PV', 'RB', 'RD', 'RF', 'RG', 'RT', 'SD', 'SE',
    'SL', 'SM', 'SN', 'SP', 'SS', 'SX', 'UB', 'VX', 'WR', 'ZD'

]


asset_specs = [
    ('Character', 'Cow'),
    ('Character', 'Dog'),
    ('Character', 'Monkey'),
    ('Character', 'Pig'),
    ('Character', 'Camel'),
    ('Character', 'Snake'),
    ('Environment', 'Moon'),
    ('Environment', 'Mars'),
    ('Environment', 'Space'),
    ('Environment', 'Forest'),
    ('Environment', 'Volcano'),
]


def full(sg):
    
    fix = Fixture(sg)
    steps = fix.default_steps()
    
    random.shuffle(project_names)
    random.shuffle(sequence_names)
    
    for proj_i in xrange(4):
        proj = fix.Project(project_names.pop())
        
        for seq_i in xrange(random.randint(3, 8)):
            seq = proj.Sequence(sequence_names.pop())
            for shot_i in xrange(random.randint(3, 8)):
                shot = seq.Shot('%s_%03d' % (seq['code'], shot_i + 1))
                for step_code in ('Online', 'MM', 'Anm', 'Light', 'Comp'):
                    shot.Task('Do %s Work' % step_code, steps[step_code])

        random.shuffle(asset_specs)
        for asset_i in xrange(random.randint(5, 9)):
            type_, code = asset_specs[asset_i]
            asset = proj.Asset(code, type_)
            
            for step_code in ('Art', 'Model', 'Rig'):
                asset.Task('Do %s Work' % step_code, steps[step_code])
            
    
    