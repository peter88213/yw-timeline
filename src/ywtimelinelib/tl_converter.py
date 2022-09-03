"""Provide a converter class for yWriter and Timeline.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw-timeline
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
from pywriter.pywriter_globals import *
from pywriter.converter.yw_cnv_ui import YwCnvUi
from pywriter.yw.yw7_file import Yw7File
from ywtimelinelib.tl_file import TlFile


class TlConverter(YwCnvUi):
    """A converter class for yWriter and Timeline.
    
    Public methods:
        run(sourcePath, **kwargs) -- create source and target objects and run conversion.
    """

    def run(self, sourcePath, **kwargs):
        """Create source and target objects and run conversion.

        Positional arguments: 
            sourcePath -- str: the source file path.

        The direction of the conversion is determined by the source file type.
        Only yWriter project files and Timeline files are accepted.
        """
        self.newFile = None
        if not os.path.isfile(sourcePath):
            self.ui.set_info_how(f'{ERROR}{_("File not found")}: "{os.path.normpath(sourcePath)}".')
            return

        fileName, fileExtension = os.path.splitext(sourcePath)
        if fileExtension == TlFile.EXTENSION:
            # Source is a timeline
            sourceFile = TlFile(sourcePath, **kwargs)
            targetFile = Yw7File(f'{fileName}{Yw7File.EXTENSION}', **kwargs)
            if os.path.isfile(f'{fileName}{Yw7File.EXTENSION}'):
                # Update existing yWriter project from timeline
                sourceFile.ywProject = targetFile
                self.import_to_yw(sourceFile, targetFile)
            else:
                # Create new yWriter project from timeline
                self.create_yw7(sourceFile, targetFile)
        elif fileExtension == Yw7File.EXTENSION:
            # Update existing timeline from yWriter project
            sourceFile = Yw7File(sourcePath, **kwargs)
            targetFile = TlFile(f'{fileName}{TlFile.EXTENSION}', **kwargs)
            targetFile.ywProject = sourceFile
            self.export_from_yw(sourceFile, targetFile)
        else:
            # Source file format is not supported
            self.ui.set_info_how(f'{ERROR}{_("File type is not supported")}: "{os.path.normpath(sourcePath)}".')
