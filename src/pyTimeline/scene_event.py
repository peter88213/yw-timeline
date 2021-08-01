"""Provide a class for Timeline scene event representation.

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw-timeline
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.model.scene import Scene


class SceneEvent(Scene):
    """Timeline scene event representation.
    """

    def __init__(self):
        """Extend the superclass method, defining a container ID.
        """
        Scene.__init__(self)
        self.contId = None
