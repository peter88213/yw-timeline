"""Provide a class for Timeline item event representation.

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw-timeline
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.model.world_element import WorldElement


class ItemEvent(WorldElement):
    """Timeline ite, event representation.
    """

    def __init__(self):
        """Extend the superclass method, defining a container ID.
        """
        WorldElement.__init__(self)
        self.contId = None
