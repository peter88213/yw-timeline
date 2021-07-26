"""Provide a converter class for a Timeline object to read and a new yWriter project.

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw-timeline
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.converter.yw_cnv_ui import YwCnvUi

from pywriter.yw.yw7_file import Yw7File
from pyTimeline.tl_file import TlFile
from pyTimeline.tl_export_target_factory import TlExportTargetFactory
from pyTimeline.tl_new_project_factory import TlNewProjectFactory


class TlConverter(YwCnvUi):
    """A converter class for timelines."""
    EXPORT_SOURCE_CLASSES = [Yw7File]
    EXPORT_TARGET_CLASSES = [TlFile]
    IMPORT_SOURCE_CLASSES = [TlFile]
    IMPORT_TARGET_CLASSES = [Yw7File]

    def __init__(self):
        """Extend the superclass constructor.

        Override newProjectFactory by a project
        specific implementation that accepts the
        .md file extension. 
        """
        YwCnvUi.__init__(self)
        self.newProjectFactory = TlNewProjectFactory()
        self.exportTargetFactory = TlExportTargetFactory()
