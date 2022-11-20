"""Provide a converter class for yWriter and Timeline.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw-timeline
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
from pywriter.pywriter_globals import *
from pywriter.converter.yw_cnv_ui import YwCnvUi
from pywriter.yw.yw7_file import Yw7File
from pywriter.model.novel import Novel
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
            self.ui.set_info_how(f'!{_("File not found")}: "{norm_path(sourcePath)}".')
            return

        fileName, fileExtension = os.path.splitext(sourcePath)
        if fileExtension == TlFile.EXTENSION:
            # Source is a timeline
            sourceFile = TlFile(sourcePath, **kwargs)
            targetFile = Yw7File(f'{fileName}{Yw7File.EXTENSION}', **kwargs)
            if os.path.isfile(f'{fileName}{Yw7File.EXTENSION}'):
                # Update existing yWriter project from timeline
                self.import_to_yw(sourceFile, targetFile)
            else:
                # Create new yWriter project from timeline
                self.create_yw7(sourceFile, targetFile)
        elif fileExtension == Yw7File.EXTENSION:
            # Update existing timeline from yWriter project
            sourceFile = Yw7File(sourcePath, **kwargs)
            targetFile = TlFile(f'{fileName}{TlFile.EXTENSION}', **kwargs)
            self.export_from_yw(sourceFile, targetFile)
        else:
            # Source file format is not supported
            self.ui.set_info_how(f'!{_("File type is not supported")}: "{norm_path(sourcePath)}".')

    def import_to_yw(self, source, target):
        """Convert from any file format to yWriter project.

        Positional arguments:
            source -- Any Novel subclass instance.
            target -- YwFile subclass instance.

        Operation:
        1. Send specific information about the conversion to the UI.
        2. Convert source into target.
        3. Pass the message to the UI.
        4. Delete the temporay file, if exists.
        5. Save the new file pathname.

        Error handling:
        - If the conversion fails, newFile is set to None.
        """
        self.ui.set_info_what(
            _('Input: {0} "{1}"\nOutput: {2} "{3}"').format(source.DESCRIPTION, norm_path(source.filePath), target.DESCRIPTION, norm_path(target.filePath)))
        self.newFile = None
        try:
            self.check(source, target)
            target.novel = Novel()
            target.read()
            source.novel = target.novel
            source.read()
            target.novel = source.novel
            target.write()
        except Error as ex:
            message = f'!{str(ex)}'
        else:
            message = f'{_("File written")}: "{norm_path(target.filePath)}".'
            self.newFile = target.filePath
            if target.scenesSplit:
                self.ui.show_warning(_('New scenes created during conversion.'))
        finally:
            self.ui.set_info_how(message)
            self._delete_tempfile(source.filePath)

