# -----------------------------------
# Unit Tests for Document Archiver
# -----------------------------------

from archive import DocumentArchiver
import textwrap
import unittest


class TestArchiveDocuments(unittest.TestCase):
    def setUp(self):
        self.archiver = DocumentArchiver(verbose=False)
    def test_simulate(self):
        moved_documents = self.archiver.simulate(max=100)
        #self.assertEqual(len(moved_documents), 100)
        for move in moved_documents:
            print(move)
    def test_destinations(self):
        self.archiver.files = [
            'TestDocument_20250624.pdf',
            'TestDocument_20250624_001.pdf',
            'TestDocument_20250624b.pdf',
            '20250624_TestDocument.pdf',
        ]
        moved_documents = self.archiver.simulate(max=100)
        expected = textwrap.dedent("""\
            Move "TestDocument_20250624.pdf" to ".../Documents/2025/TestDocument_20250624.pdf"
            Move "TestDocument_20250624_001.pdf" to ".../Documents/2025/TestDocument_20250624b.pdf"
            Move "TestDocument_20250624b.pdf" to ".../Documents/2025/TestDocument_20250624b.pdf"
            Move "20250624_TestDocument.pdf" to ".../Documents/2025/TestDocument_20250624.pdf"
            """).splitlines()
        self.assertEqual(moved_documents, expected)
    def test_existing_files(self):
        self.archiver.files = [
            'TestDocument_20250624.pdf',
            'TestDocument_20250624_001.pdf',
            'TestDocument_20250624b.pdf',
            '20250624_TestDocument.pdf',
        ]
        self.archiver.existing_files = [
            '.../Documents/2025/TestDocument_20250624.pdf',
            '.../Documents/2025/TestDocument_20250624b.pdf']
        moved_documents = self.archiver.simulate(max=100)
        expected = textwrap.dedent("""\
            Move "TestDocument_20250624.pdf" to ".../Documents/2025/TestDocument_20250624c.pdf"
            Move "TestDocument_20250624_001.pdf" to ".../Documents/2025/TestDocument_20250624c.pdf"
            Move "TestDocument_20250624b.pdf" to ".../Documents/2025/TestDocument_20250624c.pdf"
            Move "20250624_TestDocument.pdf" to ".../Documents/2025/TestDocument_20250624c.pdf"
            """).splitlines()
        self.assertEqual(moved_documents, expected)
    def test_samename(self):
        new_name = self.archiver.determine_new_name('TestDocument_20250624.pdf')
        self.assertEqual(new_name, 'TestDocument_20250624.pdf')
    def test_rename1(self):
        new_name = self.archiver.determine_new_name('TestDocument_20250624b.pdf')
        self.assertEqual(new_name, 'TestDocument_20250624b.pdf')
    def test_rename2(self):
        new_name = self.archiver.determine_new_name('TestDocument_20250624_001.pdf')
        self.assertEqual(new_name, 'TestDocument_20250624b.pdf')
    def test_rename3(self):
        new_name = self.archiver.determine_new_name('20250624_TestDocument.pdf')
        self.assertEqual(new_name, 'TestDocument_20250624.pdf')

    def test_nextname1(self):
        new_name = self.archiver.determine_next_name('TestDocument_20250624.pdf')
        self.assertEqual(new_name, 'TestDocument_20250624b.pdf')
    def test_nextname2(self):
        new_name = self.archiver.determine_next_name('TestDocument_20250624b.pdf')
        self.assertEqual(new_name, 'TestDocument_20250624c.pdf')


if __name__ == '__main__':
    unittest.main()
