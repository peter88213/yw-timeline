#!/usr/bin/env python3
"""Synchronize yWriter project with Timeline

Version @release
Requires Python 3.6+
Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw-timeline
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import argparse
from pathlib import Path
from pywriter.pywriter_globals import *
from pywriter.ui.ui import Ui
from pywriter.ui.ui_tk import UiTk
from pywriter.ui.set_icon_tk import *
from pywriter.config.configuration import Configuration
from ywtimelinelib.tl_converter import TlConverter

SUFFIX = ''
APPNAME = 'yw-timeline'
SETTINGS = dict(
    scene_label='Scene',
    default_date_time='2021-07-26 00:00:00',
    scene_color='170,240,160',
)
OPTIONS = dict(
    ignore_unspecific=False,
    dhm_to_datetime=False,
    datetime_to_dhm=False,
)


def run(sourcePath, silentMode=True, installDir='.'):
    if silentMode:
        ui = Ui('')
    else:
        ui = UiTk(f'{_("Synchronize Timeline and yWriter")} @release')
        set_icon(ui.root, icon='tLogo32')

    #--- Try to get persistent configuration data
    sourceDir = os.path.dirname(sourcePath)
    if not sourceDir:
        sourceDir = '.'
    iniFileName = f'{APPNAME}.ini'
    iniFiles = [f'{installDir}/{iniFileName}', f'{sourceDir}/{iniFileName}']
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
    try:
        homeDir = str(Path.home()).replace('\\', '/')
        installDir = f'{homeDir}/.pywriter/{APPNAME}/config'
    except:
        installDir = '.'
    run(args.sourcePath, args.silent, installDir)
