"""Timeline sync plugin for novelyst.

Version @release
Compatibility: novelyst v0.36 API 
Requires Python 3.6+
Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/aeon2yw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import sys
from pathlib import Path
import tkinter as tk
import locale
import gettext
from tkinter import messagebox
from datetime import datetime
from pywriter.pywriter_globals import *
from pywriter.config.configuration import Configuration
from pywriter.file.doc_open import open_document
from pywriter.converter.yw_cnv_ui import YwCnvUi
from ywtimelinelib.tl_file import TlFile

# Initialize localization.
LOCALE_PATH = f'{os.path.dirname(sys.argv[0])}/locale/'
CURRENT_LANGUAGE = locale.getdefaultlocale()[0][:2]
try:
    t = gettext.translation('yw-timeline_novelyst', LOCALE_PATH, languages=[CURRENT_LANGUAGE])
    _ = t.gettext
except:

    def _(message):
        return message

APPLICATION = 'Timeline'
PLUGIN = f'{APPLICATION} plugin v@release'
INI_FILENAME = 'yw-timeline.ini'
INI_FILEPATH = '.pywriter/yw-timeline/config'


class Plugin():
    """Plugin class for synchronization with Timeline.
    
    Public methods:
        disable_menu() -- disable menu entries when no project is open.
        enable_menu() -- enable menu entries when a project is open.
        
    """
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

    def __init__(self, ui):
        """Add a submenu to the main menu.
        
        Positional arguments:
            ui -- reference to the NovelystTk instance of the application.
        """
        self._ui = ui
        self._converter = YwCnvUi()
        self._converter.ui = ui

        # Create a submenu
        self._pluginMenu = tk.Menu(self._ui.mainMenu, tearoff=0)
        self._ui.mainMenu.add_cascade(label=APPLICATION, menu=self._pluginMenu)
        self._ui.mainMenu.entryconfig(APPLICATION, state='disabled')
        self._pluginMenu.add_command(label=_('Information'), command=self._info)
        self._pluginMenu.add_separator()
        self._pluginMenu.add_command(label=_('Create or update the timeline'), command=self._export_from_yw)
        self._pluginMenu.add_command(label=_('Update the project'), command=self._import_to_yw)
        self._pluginMenu.add_separator()
        self._pluginMenu.add_command(label=_('Edit the timeline'), command=self._launch_application)

    def disable_menu(self):
        """Disable menu entries when no project is open."""
        self._ui.mainMenu.entryconfig(APPLICATION, state='disabled')

    def enable_menu(self):
        """Enable menu entries when a project is open."""
        self._ui.mainMenu.entryconfig(APPLICATION, state='normal')

    def _launch_application(self):
        """Launch Timeline with the current project."""
        if self._ui.ywPrj:
            timelinePath = f'{os.path.splitext(self._ui.ywPrj.filePath)[0]}{TlFile.EXTENSION}'
            if os.path.isfile(timelinePath):
                if self._ui.lock():
                    open_document(timelinePath)
            else:
                self._ui.set_info_how(_('{0}No {1} file available for this project.').format(ERROR, APPLICATION))

    def _export_from_yw(self):
        """Update timeline from yWriter.
        """
        if self._ui.ywPrj:
            timelinePath = f'{os.path.splitext(self._ui.ywPrj.filePath)[0]}{TlFile.EXTENSION}'
            if os.path.isfile(timelinePath):
                action = _('update')
            else:
                action = _('create')
            if self._ui.ask_yes_no(_('Save the project and {} the timeline?').format(action)):
                self._ui.save_project()
                kwargs = self._get_configuration(self._ui.ywPrj.filePath)
                targetFile = TlFile(timelinePath, **kwargs)
                targetFile.ywProject = self._ui.ywPrj
                self._converter.export_from_yw(self._ui.ywPrj, targetFile)

    def _info(self):
        """Show information about the Timeline file."""
        if self._ui.ywPrj:
            timelinePath = f'{os.path.splitext(self._ui.ywPrj.filePath)[0]}{TlFile.EXTENSION}'
            if os.path.isfile(timelinePath):
                try:
                    timestamp = os.path.getmtime(timelinePath)
                    if timestamp > self._ui.ywPrj.timestamp:
                        cmp = _('newer')
                    else:
                        cmp = _('older')
                    fileDate = datetime.fromtimestamp(timestamp).replace(microsecond=0).isoformat(sep=' ')
                    message = _('{0} file is {1} than the yWriter project.\n (last saved on {2})').format(APPLICATION, cmp, fileDate)
                except:
                    message = _('Cannot determine file date.')
            else:
                message = _('No {0} file available for this project.').format(APPLICATION)
            messagebox.showinfo(PLUGIN, message)

    def _import_to_yw(self):
        """Update yWriter from timeline.
        """
        if self._ui.ywPrj:
            timelinePath = f'{os.path.splitext(self._ui.ywPrj.filePath)[0]}{TlFile.EXTENSION}'
            if os.path.isfile(timelinePath):
                if self._ui.ask_yes_no(_('Save the project and update it?')):
                    self._ui.save_project()
                    kwargs = self._get_configuration(timelinePath)
                    sourceFile = TlFile(timelinePath, **kwargs)
                    sourceFile.ywProject = self._ui.ywPrj
                    self._converter.import_to_yw(sourceFile, self._ui.ywPrj)
                    message = self._ui.infoHowText
                    self._ui.reload_project()
                    self._ui.set_info_how(message)
            else:
                self._ui.set_info_how(_('{0}No {1} file available for this project.').format(ERROR, APPLICATION))

    def _get_configuration(self, sourcePath):
        #--- Try to get persistent configuration data
        sourceDir = os.path.dirname(sourcePath)
        if not sourceDir:
            sourceDir = '.'
        try:
            homeDir = str(Path.home()).replace('\\', '/')
            pluginCnfDir = f'{homeDir}/{INI_FILEPATH}'
        except:
            pluginCnfDir = '.'
        iniFiles = [f'{pluginCnfDir}/{INI_FILENAME}', f'{sourceDir}/{INI_FILENAME}']
        configuration = Configuration(self.SETTINGS, self.OPTIONS)
        for iniFile in iniFiles:
            configuration.read(iniFile)
        kwargs = {}
        kwargs.update(configuration.settings)
        kwargs.update(configuration.options)
        return kwargs

