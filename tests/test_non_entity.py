from common import *


class TestNonEntity(TestCase):
    
    def test_connect_and_close(self):
        sg = Shotgun()
        sg.connect()
        sg.close()