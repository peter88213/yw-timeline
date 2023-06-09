"""Regression test for the yw-timeline project.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/yw-timeline
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from shutil import copyfile
import os
import unittest
import yw_timeline_

# Test environment

# The paths are relative to the "test" directory,
# where this script is placed and executed

TEST_PATH = os.getcwd() + '/../test'
TEST_DATA_PATH = TEST_PATH + '/data/'
TEST_EXEC_PATH = TEST_PATH + '/yw7/'

# Test data
TEST_YW7 = TEST_EXEC_PATH + 'yw7 Sample Project.yw7'
TEST_YW_BAK = TEST_YW7 + '.bak'
TEST_TL = TEST_EXEC_PATH + 'yw7 Sample Project.timeline'
TEST_TL_BAK = TEST_TL + '.bak'
INI_FILE = 'yw-timeline.ini'


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
        os.remove(TEST_TL_BAK)
    except:
        pass
    try:
        os.remove(TEST_YW_BAK)
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

    # @unittest.skip('')
    def test_tl_to_new_yw(self):
        copyfile(TEST_DATA_PATH + 'outline.timeline', TEST_TL)
        os.chdir(TEST_EXEC_PATH)
        yw_timeline_.run(TEST_TL, silentMode=True)
        self.assertEqual(read_file(TEST_YW7), read_file(TEST_DATA_PATH + 'normal.yw7'))
        self.assertEqual(read_file(TEST_TL), read_file(TEST_DATA_PATH + 'rewritten.timeline'))

    # @unittest.skip('')
    def test_modified_yw_to_tl(self):
        copyfile(TEST_DATA_PATH + 'normal.timeline', TEST_TL)
        copyfile(TEST_DATA_PATH + 'modified.yw7', TEST_YW7)
        os.chdir(TEST_EXEC_PATH)
        yw_timeline_.run(TEST_YW7, silentMode=True)
        self.assertEqual(read_file(TEST_TL), read_file(TEST_DATA_PATH + 'modified.timeline'))
        self.assertEqual(read_file(TEST_TL_BAK), read_file(TEST_DATA_PATH + 'normal.timeline'))

    # @unittest.skip('')
    def test_modified2_tl_to_yw(self):
        copyfile(TEST_DATA_PATH + 'modified2.timeline', TEST_TL)
        copyfile(TEST_DATA_PATH + 'modified.yw7', TEST_YW7)
        os.chdir(TEST_EXEC_PATH)
        yw_timeline_.run(TEST_TL, silentMode=True)
        self.assertEqual(read_file(TEST_YW7), read_file(TEST_DATA_PATH + 'modified2.yw7'))
        self.assertEqual(read_file(TEST_YW_BAK), read_file(TEST_DATA_PATH + 'modified.yw7'))

    # @unittest.skip('')
    def test_modified_yw_to_new_tl(self):
        copyfile(TEST_DATA_PATH + 'modified.yw7', TEST_YW7)
        os.chdir(TEST_EXEC_PATH)
        yw_timeline_.run(TEST_YW7, silentMode=True)
        self.assertEqual(read_file(TEST_TL), read_file(TEST_DATA_PATH + 'new.timeline'))

    # @unittest.skip('')
    def test_dateTimeToDhm(self):
        copyfile(TEST_DATA_PATH + 'normal.yw7', TEST_YW7)
        copyfile(TEST_DATA_PATH + 'dateTimeToDhm.ini', TEST_EXEC_PATH + INI_FILE)
        os.chdir(TEST_EXEC_PATH)
        yw_timeline_.run(TEST_YW7, silentMode=True)
        yw_timeline_.run(TEST_TL, silentMode=True)
        self.assertEqual(read_file(TEST_YW7), read_file(TEST_DATA_PATH + 'dateTimeToDhm.yw7'))

    # @unittest.skip('')
    def test_dhmToDateTime(self):
        copyfile(TEST_DATA_PATH + 'dateTimeToDhm.yw7', TEST_YW7)
        copyfile(TEST_DATA_PATH + 'dhmToDateTime.ini', TEST_EXEC_PATH + INI_FILE)
        os.chdir(TEST_EXEC_PATH)
        yw_timeline_.run(TEST_YW7, silentMode=True)
        yw_timeline_.run(TEST_TL, silentMode=True)
        self.assertEqual(read_file(TEST_YW7), read_file(TEST_DATA_PATH + 'dhmToDateTime.yw7'))

    def tearDown(self):
        remove_all_testfiles()


def main():
    unittest.main()


if __name__ == '__main__':
    main()
