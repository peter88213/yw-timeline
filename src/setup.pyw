"""Install the yw-timeline script and set up the registry files
for extending the yWriter and Timeline context menus. 

Version @release

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw-timeline
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import sys
from string import Template
from shutil import copyfile
from pathlib import Path


APP = 'yw-timeline.pyw'
INI_PATH = '/config/'
SAMPLE_PATH = 'sample/'
INI_FILE = 'yw-timeline.ini'

YW_CONTEXT_MENU = '''Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\SOFTWARE\Classes\\yWriter7\\shell\\Export to Timeline]

[HKEY_CURRENT_USER\SOFTWARE\Classes\\yWriter7\\shell\\Export to Timeline\\command]
@="\\"${PYTHON}\\" \\"${SCRIPT}\\" \\"%1\\""

[HKEY_CURRENT_USER\\SOFTWARE\\Classes\\.timeline]
@="TimelineProject"

[HKEY_CURRENT_USER\\SOFTWARE\\Classes\\TimelineProject]
@="Timeline Project"

[HKEY_CURRENT_USER\\SOFTWARE\\Classes\\TimelineProject\\DefaultIcon]
@="C:\\\\Program Files (x86)\\\\Timeline\\\\timeline.exe,0"

[HKEY_CURRENT_USER\\SOFTWARE\\Classes\\TimelineProject\\shell\\open]

[HKEY_CURRENT_USER\\SOFTWARE\\Classes\\TimelineProject\\shell\\open\\command]
@="\\"C:\\\\Program Files (x86)\\\\Timeline\\\\timeline.exe\\" \\"%1\\""

[HKEY_CURRENT_USER\SOFTWARE\Classes\\TimelineProject\\shell\\Export to yWriter]

[HKEY_CURRENT_USER\SOFTWARE\Classes\\TimelineProject\\shell\\Export to yWriter\\command]
@="\\"${PYTHON}\\" \\"${SCRIPT}\\" \\"%1\\""
'''

RESET_CONTEXT_MENU = '''Windows Registry Editor Version 5.00

[-HKEY_CURRENT_USER\\SOFTWARE\\Classes\\yWriter7\\shell\Export to Timeline]
[-HKEY_CURRENT_USER\\SOFTWARE\\Classes\\.timeline]
[-HKEY_CURRENT_USER\\SOFTWARE\\Classes\\TimelineProject]
'''


def update_reg(installPath):

    def make_reg(filePath, template, mapping):
        """Create a registry file to extend the yWriter context menu."""

        with open(filePath, 'w', encoding='utf-8') as f:
            f.write(template.safe_substitute(mapping))

        print(os.path.normpath(filePath) + ' written.')

    python = sys.executable.replace('\\', '\\\\')
    script = installPath.replace('/', '\\\\') + '\\\\' + APP
    mapping = dict(PYTHON=python, SCRIPT=script)
    make_reg(installPath + '/add_context_menu.reg',
             Template(YW_CONTEXT_MENU), mapping)
    make_reg(installPath + '/rem_context_menu.reg',
             Template(RESET_CONTEXT_MENU), {})


def run():
    """Install the yw-timeline script and extend the yWriter context menu."""
    installPath = str(Path.home()).replace('\\', '/') + '/.pywriter/yw-timeline'
    os.makedirs(installPath + '/config', exist_ok=True)

    with os.scandir(installPath) as files:

        for file in files:

            if not 'config' in file.name:
                os.remove(file)

    update_reg(installPath)

    copyfile(APP, installPath + '/' + APP)
    print(os.path.normpath(installPath + '/' + APP) + ' copied.')

    if not os.path.isfile(installPath + INI_PATH + INI_FILE):
        copyfile(SAMPLE_PATH + INI_FILE, installPath + INI_PATH + INI_FILE)

    os.startfile(os.path.normpath(installPath))


if __name__ == '__main__':
    run()
