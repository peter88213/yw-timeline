"""Generate German translation files for GNU gettext.

- Update the project's 'de.po' translation file.
- Generate the language specific 'pywriter.mo' dictionary.

Usage: 
translate_de.py

File structure:

├── PyWriter/
│   ├── i18n/
│   │   └── de.json
│   └── src/
│       ├── translations.py
│       └── msgfmt.py
└── yw-timeline/
    ├── src/ 
    │   └── translate_de.py
    └── i18n/
        ├── messages.pot
        ├── de.po
        ├── locale/
        │   └─ de/
        │      └─ LC_MESSAGES/
        │         └─ pywriter.mo
        └── plugin_locale/
            └─ de/
               └─ LC_MESSAGES/
                  └─ yw-timeline_novelyst.mo
    
Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw-timeline
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import sys
sys.path.insert(0, f'{os.getcwd()}/../../PyWriter/src')
import translations
from shutil import copyfile
import msgfmt

APP_NAME = 'yw-timeline'
PO_PATH = '../i18n/de.po'
MO_PATH = '../i18n/locale/de/LC_MESSAGES/pywriter.mo'
PLUGIN_NAME = f'{APP_NAME}_novelyst'
PLUGIN_MO_PATH = f'../i18n/plugin_locale/de/LC_MESSAGES/{PLUGIN_NAME}.mo'
MO_COPY = f'../../novelyst/src/locale/de/LC_MESSAGES/{PLUGIN_NAME}.mo'


def main(version='unknown'):
    if translations.main('de', app=APP_NAME, appVersion=version):
        print(f'Writing "{MO_PATH}" ...')
        msgfmt.make(PO_PATH, MO_PATH)
        copyfile(MO_PATH, PLUGIN_MO_PATH)
        copyfile(PLUGIN_MO_PATH, MO_COPY)
    else:
        sys.exit(1)


if __name__ == '__main__':
    try:
        main(sys.argv[1])
    except:
        main()
