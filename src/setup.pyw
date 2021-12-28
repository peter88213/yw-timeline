"""Install the yw-timeline script and set up the registry files
for extending the yWriter and Timeline context menus. 

Version @release

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw-timeline
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import sys
import os
from shutil import copyfile
from pathlib import Path
from tkinter import messagebox
from string import Template


APPNAME = 'yw-timeline'

APP = APPNAME + '.pyw'
INI_FILE = APPNAME + '.ini'
INI_PATH = '/config/'
SAMPLE_PATH = 'sample/'
MESSAGE = '''The $Appname program is installed here:
$Apppath

Now you might want to create a shortcut on your desktop.  

On Windows, open the installation folder clicking "Ok", hold down the Alt key on your keyboard, and then drag and drop $Appname.pyw to your desktop.

On Linux, create a launcher on your desktop. With xfce for instance, the launcher's command may look like this:
python3 '$Apppath' %F
'''


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


def run(pywriterPath):
    """Install the script."""

    # Create a general PyWriter installation directory, if necessary.

    os.makedirs(pywriterPath, exist_ok=True)
    installDir = pywriterPath + APPNAME
    cnfDir = installDir + INI_PATH

    try:
        # Move an existing installation to the new place, if necessary.

        oldInstDir = os.getenv('APPDATA').replace('\\', '/') + '/pyWriter/' + APPNAME
        os.replace(oldInstDir, installDir)

    except:
        pass

    os.makedirs(cnfDir, exist_ok=True)

    # Delete the old version, but retain configuration, if any.

    with os.scandir(installDir) as files:

        for file in files:

            if not 'config' in file.name:
                os.remove(file)

    # Install the new version.

    copyfile(APP, installDir + '/' + APP)

    # Install a configuration file, if needed.

    try:
        if not os.path.isfile(cnfDir + INI_FILE):
            copyfile(SAMPLE_PATH + INI_FILE, cnfDir + INI_FILE)

    except:
        pass

    # Generate registry entries for the context menu.

    update_reg(installDir)

    # Display a message and optionally open the installation folder for shortcut creation.

    mapping = {'Appname': APPNAME, 'Apppath': installDir + '/' + APP}

    if messagebox.askokcancel(APPNAME, Template(MESSAGE).safe_substitute(mapping)):
        os.startfile(os.path.normpath(installDir))


if __name__ == '__main__':
    pywriterPath = str(Path.home()).replace('\\', '/') + '/.pywriter/'
    run(pywriterPath)
