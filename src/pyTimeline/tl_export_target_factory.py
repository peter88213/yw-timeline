"""Provide a factory class for a Timeline object to write.

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/PyWriter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os

from pywriter.converter.file_factory import FileFactory
from pyTimeline.tl_file import TlFile


class TlExportTargetFactory(FileFactory):
    """A factory class that instantiates a document object to write."""

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a target object for conversion from a yWriter project.
        Override the superclass method.
        """
        fileName, fileExtension = os.path.splitext(sourcePath)
        suffix = kwargs['suffix']

        if suffix is None:
            suffix = ''

        targetFile = TlFile(fileName + suffix + TlFile.EXTENSION, **kwargs)
        return 'SUCCESS', None, targetFile
