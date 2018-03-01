import json
import shutil
import tempfile
import datetime
from common import *

type_ = 'Dummy' + mini_uuid().upper()

class TestJsonDbSource(TestCase):

    def test_json_save_and_load(self):
        sgSource = Shotgun()
        # Create some test values
        adate = datetime.date.today() + datetime.timedelta(days=3)
        spec = dict(name=mini_uuid(), id=10, adate=adate)
        proj1 = sgSource.create(type_, spec, return_fields=['name', 'created_at'])

        spec = dict(name=mini_uuid(), id=5)
        proj2 = sgSource.create(type_, spec)

        spec = dict(name=mini_uuid()) # id should be 11
        proj3 = sgSource.create(type_, spec)

        def validateDatabase(sg):
            entity1 = sg.find_one(type_, [['id', 'is', 10]], ['name', 'created_at', 'adate'])
            entity2 = sg.find_one(type_, [['id', 'is', 5]], ['name'])
            entity3 = sg.find_one(type_, [['id', 'is', 11]], ['name'])

            # Verify that the found entity is the same as originally created
            self.assertSameEntity(proj1, entity1)
            self.assertSameEntity(proj2, entity2)
            self.assertSameEntity(proj3, entity3)

            # Check that extra fields are the same.
            msg = 'Source name: {s} does not match dest name: {d}'
            self.assertEqual(proj1['name'], entity1['name'],
                msg.format(s=proj1['name'], d=entity1['name']))
            self.assertEqual(proj2['name'], entity2['name'],
                msg.format(s=proj1['name'], d=entity1['name']))
            self.assertEqual(proj3['name'], entity3['name'],
                msg.format(s=proj1['name'], d=entity1['name']))

            # Check that datetime.datetime objects were restored correctly
            msg = 'Source datetime: {s} does not match dest datetime: {d}'
            self.assertEqual(proj1['created_at'], entity1['created_at'],
                msg.format(s=proj1['created_at'], d=entity1['created_at']))

            # Check that datetime.date objects were restored correctly
            msg = 'Source date: {s} does not match dest date: {d}'
            self.assertEqual(adate, entity1['adate'],
                msg.format(s=adate, d=entity1['adate']))
            self.assertEqual(proj1['adate'], entity1['adate'],
                msg.format(s=proj1['adate'], d=entity1['adate']))

        # Validate that our source db is setup as expected
        validateDatabase(sgSource)

        with tempfile.TemporaryFile(prefix='sgmock_') as fp:
            # Save the source db to disk.
            sgSource.sgmock_json_dump(fp, indent=4)

            # Create a new empty shotgun connection and db
            sgDest = Shotgun()
            self.assertEqual(len(sgDest._store), 0)

            # Move to the beginning of the tempfile so we can read it
            fp.seek(0)
            # import the json data from file to the new db.
            sgDest.sgmock_json_load(fp)

        # validate that the new db was properly loaded from json data
        validateDatabase(sgDest)

        # Ensure the id index is updated to the largest created entity id
        self.assertEqual(sgDest._ids[type_], 11)
