"""Provide a class for Timeline item event representation.

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw-timeline
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import xml.etree.ElementTree as ET
from pywriter.model.world_element import WorldElement
from pyTimeline.dt_helper import fix_iso_dt


class ItemEvent(WorldElement):
    """Timeline ite, event representation.
    """

    # Class variables (to be initialized externally).

    defaultDateTime = None
    itemMarker = None

    def __init__(self):
        """Extend the superclass method, defining a container ID.
        """
        WorldElement.__init__(self)
        self.contId = None

    def build_subtree(self, xmlEvent, itId, dtMin, dtMax):
        """Write item properties to the xmlEvent subtree.
        Return maximum and minimum date/time.
        """
        scIndex = 0

        if xmlEvent.find('start') is None:
            ET.SubElement(xmlEvent, 'start').text = self.defaultDateTime

        startDateTime = fix_iso_dt(xmlEvent.find('start').text)

        if (not dtMin) or (startDateTime < dtMin):
            dtMin = startDateTime

        scIndex += 1

        if xmlEvent.find('end') is None:
            ET.SubElement(xmlEvent, 'end').text = self.defaultDateTime

        endDateTime = fix_iso_dt(xmlEvent.find('end').text)

        if (not dtMax) or (endDateTime > dtMax):
            dtMax = endDateTime

        scIndex += 1

        if not self.title:
            self.title = 'Unnamed item ID' + itId

        try:
            xmlEvent.find('text').text = self.title

        except(AttributeError):
            ET.SubElement(xmlEvent, 'text').text = self.title

        scIndex += 1

        if xmlEvent.find('progress') is None:
            ET.SubElement(xmlEvent, 'progress').text = '0'

        scIndex += 1

        if xmlEvent.find('fuzzy') is None:
            ET.SubElement(xmlEvent, 'fuzzy').text = 'False'

        scIndex += 1

        if xmlEvent.find('locked') is None:
            ET.SubElement(xmlEvent, 'locked').text = 'False'

        scIndex += 1

        if xmlEvent.find('ends_today') is None:
            ET.SubElement(xmlEvent, 'ends_today').text = 'False'

        scIndex += 1

        try:
            xmlEvent.find('category').text = self.itemMarker

        except:
            ET.SubElement(xmlEvent, 'category').text = self.itemMarker

        scIndex += 1

        if self.desc is not None:

            try:
                xmlEvent.find('description').text = self.desc

            except(AttributeError):

                if xmlEvent.find('labels') is None:

                    # Append the description.

                    ET.SubElement(xmlEvent, 'description').text = self.desc

                else:
                    # Insert the description.

                    desc = ET.Element('description')
                    desc.text = self.desc
                    xmlEvent.insert(scIndex, desc)

        elif xmlEvent.find('description') is not None:
            xmlEvent.remove(xmlEvent.find('description'))

        if xmlEvent.find('labels') is None:
            ET.SubElement(xmlEvent, 'labels').text = 'ItemID:' + itId

        if xmlEvent.find('default_color') is None:
            ET.SubElement(xmlEvent, 'default_color').text = '192,192,192'

        return dtMin, dtMax
