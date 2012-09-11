from common import *


class TestBatch(TestCase):
    
    def test_batch_create(self):
        
        type_ = 'Dummy' + mini_uuid().upper()
        count = 5
        
        sg = Shotgun()
        result = sg.batch([dict(
            request_type='create',
            entity_type=type_,
            data=dict(i=i),
        ) for i in xrange(count)])
        
        self.assertEqual(len(result), count)
        for entity in result:
            found = sg.find(type_, [('id', 'is', entity['id'])])
            self.assertEqual(1, len(found))
            self.assertSameEntity(entity, found[0])
            self.assertIsNot(entity, found[0])
        