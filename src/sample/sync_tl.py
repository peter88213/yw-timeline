"""Synchronize yWriter project with Timeline

This is a yw-timeline sample application.

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw2md
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
SUFFIX = ''
DEFAULT_DATE_TIME = '2021-07-26 00:00:00'

import sys

from pywriter.ui.ui_tk import UiTk
from pyTimeline.tl_converter import TlConverter


def run(sourcePath, suffix=None):
    ui = UiTk('Timeline sync with yWriter')
    converter = TlConverter()
    converter.ui = ui
    kwargs = {'suffix': suffix, 'sceneMarker': 'Scene',
              'defaultDateTime': DEFAULT_DATE_TIME}
    converter.run(sourcePath, **kwargs)
    ui.start()


if __name__ == '__main__':
    run(sys.argv[1], SUFFIX)
