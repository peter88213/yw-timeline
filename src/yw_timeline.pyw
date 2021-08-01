#!/usr/bin/env python3
"""Synchronize yWriter project with Timeline

Version @release
Requires Python 3.7 or above

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw-timeline
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import argparse

from pywriter.ui.ui import Ui
from pywriter.ui.ui_tk import UiTk
from pywriter.config.configuration import Configuration

from pyTimeline.tl_converter import TlConverter


SUFFIX = ''
APPNAME = 'yw-timeline'

SETTINGS = dict(
    scene_label='Scene',
    item_category='Item',
    default_date_time='2021-07-26 00:00:00',
    scene_color='170,240,160',
    item_color='160,230,250',
)
OPTIONS = dict(
    ignore_items=False,
    ignore_unspecific=False,
    single_backup=True,
)


def run(sourcePath, silentMode=True):

    if silentMode:
        ui = Ui('')

    else:
        ui = UiTk('Synchronize yWriter with Timeline @release')

    #--- Try to get persistent configuration data

    sourceDir = os.path.dirname(sourcePath)

    if sourceDir == '':
        sourceDir = './'

    else:
        sourceDir += '/'

    installDir = os.getenv('APPDATA').replace('\\', '/') + '/pyWriter/' + APPNAME + '/config/'
    iniFileName = APPNAME + '.ini'
    iniFiles = [installDir + iniFileName, sourceDir + iniFileName]

    configuration = Configuration(SETTINGS, OPTIONS)

    for iniFile in iniFiles:
        configuration.read(iniFile)

    kwargs = {'suffix': SUFFIX}
    kwargs.update(configuration.settings)
    kwargs.update(configuration.options)

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

    run(args.sourcePath, args.silent)
