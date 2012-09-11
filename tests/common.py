from pprint import pprint
from unittest import TestCase as BaseTestCase
import os

import shotgun_api3

from sgmock import Shotgun, ShotgunError, Fault
from sgmock import Fixture
from sgmock import TestCase

def mini_uuid():
    return os.urandom(4).encode('hex')



