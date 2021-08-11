""" Python unit tests for the yw-timeline project.

Test suite for yw-timeline.pyw.

For further information see https://github.com/peter88213/yw-timeline
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from shutil import copyfile
import os
import unittest
import _yw_timeline


# Test environment

# The paths are relative to the "test" directory,
# where this script is placed and executed

TEST_PATH = os.getcwd() + '/../test'
TEST_DATA_PATH = TEST_PATH + '/data/'
TEST_EXEC_PATH = TEST_PATH + '/yw7/'

# To be placed in TEST_DATA_PATH:
NORMAL_YW7 = TEST_DATA_PATH + 'normal.yw7'
NORMAL_TL = TEST_DATA_PATH + 'normal.timeline'
MODIFIED_YW7 = TEST_DATA_PATH + 'modified.yw7'
MODIFIED2_YW7 = TEST_DATA_PATH + 'modified2.yw7'
MODIFIED_TL = TEST_DATA_PATH + 'modified.timeline'
MODIFIED2_TL = TEST_DATA_PATH + 'modified2.timeline'
NEW_TL = TEST_DATA_PATH + 'new.timeline'
INI_FILE = 'yw-timeline.ini'

# Test data
TEST_YW7 = TEST_EXEC_PATH + 'yw7 Sample Project.yw7'
TEST_TL = TEST_EXEC_PATH + 'yw7 Sample Project.timeline'
BACKUP_TL = TEST_TL + '.bak'
BACKUP_YW7 = TEST_YW7 + '.bak'


def read_file(inputFile):
    try:
        with open(inputFile, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        # HTML files exported by a word processor may be ANSI encoded.
        with open(inputFile, 'r') as f:
            return f.read()


def remove_all_testfiles():

    try:
        os.remove(TEST_YW7)

    except:
        pass

    try:
        os.remove(TEST_TL)
    except:
        pass

    try:
        os.remove(TEST_EXEC_PATH + INI_FILE)
    except:
        pass

    try:
        os.remove(BACKUP_TL)
    except:
        pass

    try:
        os.remove(BACKUP_YW7)
    except:
        pass


class NormalOperation(unittest.TestCase):
    """Test case: Normal operation."""

    def setUp(self):

        try:
            os.mkdir(TEST_EXEC_PATH)

        except:
            pass

        remove_all_testfiles()
        copyfile(TEST_DATA_PATH + INI_FILE, TEST_EXEC_PATH + INI_FILE)

    def test_tl_to_new_yw(self):
        copyfile(NORMAL_TL, TEST_TL)
        os.chdir(TEST_EXEC_PATH)
        _yw_timeline.run(TEST_TL, silentMode=True)
        self.assertEqual(read_file(TEST_YW7), read_file(NORMAL_YW7))

    def test_modified_yw_to_tl(self):
        copyfile(NORMAL_TL, TEST_TL)
        copyfile(MODIFIED_YW7, TEST_YW7)
        os.chdir(TEST_EXEC_PATH)
        _yw_timeline.run(TEST_YW7, silentMode=True)
        self.assertEqual(read_file(TEST_TL), read_file(MODIFIED_TL))
        self.assertEqual(read_file(BACKUP_TL), read_file(NORMAL_TL))

    def test_modified2_tl_to_yw(self):
        copyfile(MODIFIED2_TL, TEST_TL)
        copyfile(MODIFIED_YW7, TEST_YW7)
        os.chdir(TEST_EXEC_PATH)
        _yw_timeline.run(TEST_TL, silentMode=True)
        self.assertEqual(read_file(TEST_YW7), read_file(MODIFIED2_YW7))
        self.assertEqual(read_file(BACKUP_YW7), read_file(MODIFIED_YW7))

    def test_modified_yw_to_new_tl(self):
        copyfile(MODIFIED_YW7, TEST_YW7)
        os.chdir(TEST_EXEC_PATH)
        _yw_timeline.run(TEST_YW7, silentMode=True)
        self.assertEqual(read_file(TEST_TL), read_file(NEW_TL))

    def tearDown(self):
        remove_all_testfiles()


def main():
    unittest.main()


if __name__ == '__main__':
    main()
