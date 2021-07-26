"""Provide a factory class for a document object to read and a new yWriter project.

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw-timeline
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os

from pywriter.converter.file_factory import FileFactory

from pywriter.yw.yw7_file import Yw7File
from pyTimeline.tl_file import TlFile


class TlNewProjectFactory(FileFactory):
    """A factory class that instantiates a Timeline object to read, 
    and a new yWriter project.
    """

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a source and a target object for creation of a new yWriter project.
        Override the superclass method.
        """

        fileName, fileExtension = os.path.splitext(sourcePath)
        targetFile = Yw7File(fileName + Yw7File.EXTENSION, **kwargs)

        if fileExtension == TlFile.EXTENSION:
            sourceFile = TlFile(sourcePath, **kwargs)
            return 'SUCCESS', sourceFile, targetFile

        else:
            return 'ERROR: File type of  "' + os.path.normpath(sourcePath) + '" not supported.', None, None
