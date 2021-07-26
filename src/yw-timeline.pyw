#!/usr/bin/env python3
"""Synchronize yWriter project with Timeline

Version @release
Requires Python 3.7 or above

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw-timeline
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import argparse


SUFFIX = ''
SCENE_MARKER = 'Scene'
DEFAULT_DATE_TIME = '2021-07-26 00:00:00'


from pywriter.ui.ui_tk import UiTk
from pyTimeline.tl_converter import TlConverter


def run(sourcePath, silentMode=True):

    if silentMode:
        ui = Ui('')

    else:
        ui = UiTk('Synchronize yWriter with Timeline @release')

    kwargs = dict(
        suffix=SUFFIX,
        sceneMarker=SCENE_MARKER,
        defaultDateTime=DEFAULT_DATE_TIME
    )
    converter = TlConverter()
    converter.ui = ui
    converter.run(sourcePath, **kwargs)
    ui.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Synchronize yWriter with Timeline',
        epilog='')
    parser.add_argument('sourcePath',
                        metavar='Sourcefile',
                        help='The path of the yWriter/Timeline project file.')

    parser.add_argument('--silent',
                        action="store_true",
                        help='suppress error messages and the request to confirm overwriting')
    args = parser.parse_args()

    if args.silent:
        silentMode = True

    else:
        silentMode = False

    run(args.sourcePath, silentMode)
