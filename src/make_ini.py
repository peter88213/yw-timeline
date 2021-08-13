#!/usr/bin/env python3
"""Helper file for yw-timeline test.

Create config file.

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw2xtg
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import sys
import os

from pywriter.config.configuration import Configuration
from _yw_timeline import SETTINGS
from _yw_timeline import OPTIONS
from _yw_timeline import APPNAME


def run(iniFile):
    iniDir = os.path.dirname(iniFile)

    if not os.path.isdir(iniDir):
        os.makedirs(iniDir)

    configuration = Configuration(SETTINGS, OPTIONS)
    configuration.write(iniFile)

    print(iniFile + ' written.')


if __name__ == '__main__':

    try:
        iniFile = sys.argv[1]

    except:
        iniFile = './' + APPNAME + '.ini'

    run(iniFile)
