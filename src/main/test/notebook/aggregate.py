from unittest import TestCase

from notebook.aggregate import FolderPath


class TestFolderPathTest(TestCase):
    def test_from_string(self):
        self.assertEqual(FolderPath(['Foo', 'Bar']), FolderPath.from_string('Foo/Bar'))
        self.assertEqual(FolderPath([]), FolderPath.from_string(''))
        self.assertEqual(FolderPath([]), FolderPath.from_string(None))
