# -----------------------------------
# Unit Tests for Document Archiver
# -----------------------------------

from archive import DocumentArchiver, Verbosity
import textwrap
import unittest


class TestArchiveDocuments(unittest.TestCase):
    def setUp(self):
        self.archiver = DocumentArchiver(verbose=Verbosity.SILENT)
        self.simulated_files = [
            'TestDocument_20250624.pdf',
            'TestDocument_20240624_001.pdf',
            'TestDocument_20250624b.pdf',
            '20250624_TestDocument.pdf',
        ]
    def assertMultiLineEqual(self, first, second, msg=None):
        """Overrule assertMultiLineEqual to dedent the arguments, allowing a direct usage
        of multiline strings in a simple way.
        Ignores leading and trailing whitespace and newlines."""
        first = textwrap.dedent(first).strip()
        second = textwrap.dedent(second).strip()
        return super().assertMultiLineEqual(first, second, msg)
    def test_simulate(self):
        moved_documents = self.archiver.simulate(max=100)
        for move in moved_documents:
            print(move)
    def test_destinations(self):
        self.archiver.files = self.simulated_files
        moved_documents = self.archiver.simulate(max=100)
        expected = """
            Move "TestDocument_20250624.pdf" to ".../Documents/2025/TestDocument_20250624.pdf"
            Move "TestDocument_20240624_001.pdf" to ".../Documents/2024/TestDocument_20240624b.pdf"
            Move "TestDocument_20250624b.pdf" to ".../Documents/2025/TestDocument_20250624b.pdf"
            Move "20250624_TestDocument.pdf" to ".../Documents/2025/TestDocument_20250624.pdf"
            """
        self.assertEqual('\n'.join(moved_documents), expected)
    def test_existing_files(self):
        self.archiver.files = self.simulated_files
        self.archiver.existing_files = [
            '.../Documents/2025/TestDocument_20250624.pdf',
            '.../Documents/2025/TestDocument_20250624b.pdf',
            '.../Documents/2024/TestDocument_20240624b.pdf']
        moved_documents = self.archiver.simulate(max=100)
        expected = """
            Move "TestDocument_20250624.pdf" to ".../Documents/2025/TestDocument_20250624c.pdf"
            Move "TestDocument_20240624_001.pdf" to ".../Documents/2024/TestDocument_20240624c.pdf"
            Move "TestDocument_20250624b.pdf" to ".../Documents/2025/TestDocument_20250624c.pdf"
            Move "20250624_TestDocument.pdf" to ".../Documents/2025/TestDocument_20250624c.pdf"
            """
        self.assertEqual('\n'.join(moved_documents), expected)
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

    def test_destination_dirs(self):
        self.archiver.files = self.simulated_files
        self.archiver.simulate()
        expected_report = """
            Moved 1 file to 2024
            Moved 3 files to 2025
            """
        self.assertEqual(self.archiver.create_destination_report(), expected_report)


if __name__ == '__main__':
    unittest.main()
