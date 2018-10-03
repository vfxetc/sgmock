from common import *


class TestCreateWithId(TestCase):

    def test_create_default_return(self):
        sg = Shotgun()
        type_ = 'Dummy' + mini_uuid().upper()

        # Verify that the Shotgun._id index is reset
        self.assertEqual(sg._ids[type_], 0)

        # Create a entity with a specific id
        spec = dict(name=mini_uuid(), id=10)
        proj = sg.create(type_, spec)
        self.assertEqual(proj['id'], 10)
        # It should have updated the Shotgun._id index
        self.assertEqual(sg._ids[type_], 10)

        # Create a entity with a smaller id.
        spec = dict(name=mini_uuid(), id=5)
        proj1 = sg.create(type_, spec)
        self.assertEqual(proj1['id'], 5)
        # It should not have updated the Shotgun._id index
        self.assertEqual(sg._ids[type_], 10)

        # Creating a new entity without passing in id should increment the index
        spec = dict(name=mini_uuid())
        proj = sg.create(type_, spec)
        self.assertEqual(proj['id'], 11)
        self.assertEqual(sg._ids[type_], 11)

        # Verify that creating a new record with a duplicate id is not allowed.
        spec = dict(name=mini_uuid(), id=10)
        self.assertRaises(ShotgunError, sg.create, type_, spec)

        # Verify that update ignores the id value if passed in data
        spec = dict(name=mini_uuid(), id=3)
        updated = sg.update(type_, 10, spec)
        self.assertEqual(updated['id'], 10)
        self.assertEqual(updated['name'], spec['name'])
        self.assertNotEqual(updated['name'], proj['name'])
        # Verify that the id index was not updated
        self.assertEqual(sg._ids[type_], 11)
