"""Provide a class for Timeline scene event representation.

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw-timeline
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import xml.etree.ElementTree as ET
from datetime import datetime
from datetime import timedelta
from pywriter.model.scene import Scene


class SceneEvent(Scene):
    """Timeline scene event representation.
    """
    defaultDateTime = '2021-07-26 00:00:00'
    sceneColor = '170,240,160'

    def __init__(self):
        """Extend the superclass method, defining a container ID.
        """
        Scene.__init__(self)
        self.contId = None
        self.startDate = None
        self.startTime = None
        self.endDateTime = None

    def set_date_time(self, startDateTime, endDateTime):
        """Set date/time and, if applicable, duration.
        Because yWriter can not process two-figure years, 
        they are saved for Timeline use and replaced with 
        a 'default negative date' for yWriter use.
        """
        dtIsValid = True
        # The date/time combination is within the range yWriter can process.

        # Prevent two-figure years from becoming "completed" by yWriter.

        dt = startDateTime.split(' ')

        if dt[0].startswith('-'):
            startYear = -1 * int(dt[0].split('-')[1])
            dtIsValid = False
            # "BC" year (yWriter won't process it).

        else:
            startYear = int(dt[0].split('-')[0])

        if startYear < 100:

            # Substitute date/time, so yWriter would not prefix them with '19' or '20'.

            self.date = '-0001-01-01'
            self.time = '00:00:00'
            self.startDate = dt[0]
            self.startTime = dt[1]
            dtIsValid = False
            # Two-figure year.

        else:
            self.date = dt[0]
            self.time = dt[1]

        if dtIsValid:

            # Calculate duration of scenes that begin after 99-12-31.

            sceneStart = datetime.fromisoformat(startDateTime)
            sceneEnd = datetime.fromisoformat(endDateTime)
            sceneDuration = sceneEnd - sceneStart
            self.lastsDays = str(sceneDuration.days)
            lastsHours = sceneDuration.seconds // 3600
            lastsMinutes = (sceneDuration.seconds % 3600) // 60
            self.lastsHours = str(lastsHours)
            self.lastsMinutes = str(lastsMinutes)

        else:

            # Save scene end date/time for Timeline use.

            self.endDateTime = endDateTime

    def get_startDateTime(self, defaultDateTime):
        """Return the event's start date/time stamp for Timeline use.
        """

        if self.date is not None:
            startDateTime = self.date + ' '

            if not self.time:
                startDateTime += '00:00:00'

            else:
                startDateTime += self.time

        else:
            startDateTime = defaultDateTime

        return startDateTime

    def get_endDateTime(self, startDateTime):
        """Return the event's end date/time stamp for Timeline use,
        calculated from the scene duration.
        """

        if self.endDateTime is not None and self.endDateTime > startDateTime:
            endDateTime = self.endDateTime

        elif self.lastsDays or self.lastsHours or self.lastsMinutes:

            if self.lastsDays:
                lastsDays = int(self.lastsDays)

            else:
                lastsDays = 0

            if self.lastsHours:
                lastsSeconds = int(self.lastsHours) * 3600

            else:
                lastsSeconds = 0

            if self.lastsMinutes:
                lastsSeconds += int(self.lastsMinutes) * 60

            sceneDuration = timedelta(days=lastsDays, seconds=lastsSeconds)
            sceneStart = datetime.fromisoformat(startDateTime)
            sceneEnd = sceneStart + sceneDuration
            endDateTime = sceneEnd.isoformat(' ')

            if startDateTime > endDateTime:
                endDateTime = startDateTime

        else:
            endDateTime = startDateTime

        return endDateTime

    def build_subtree(self, xmlEvent, scId, dtMin, dtMax):
        scIndex = 0

        startDateTime = self.get_startDateTime(self.defaultDateTime)

        try:
            xmlEvent.find('start').text = startDateTime

        except(AttributeError):
            ET.SubElement(xmlEvent, 'start').text = startDateTime

        if (not dtMin) or (startDateTime < dtMin):
            dtMin = startDateTime

        scIndex += 1

        endDateTime = self.get_endDateTime(startDateTime)

        try:
            xmlEvent.find('end').text = endDateTime

        except(AttributeError):
            ET.SubElement(xmlEvent, 'end').text = endDateTime

        if (not dtMax) or (endDateTime > dtMax):
            dtMax = endDateTime

        scIndex += 1

        if not self.title:
            self.title = 'Unnamed scene ID' + scId

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

        if self.desc is not None:

            try:
                xmlEvent.find('description').text = self.desc

            except(AttributeError):

                if xmlEvent.find('labels') is None:

                    # Append the description.

                    ET.SubElement(xmlEvent, 'description').text = self.desc

                else:
                    # Insert the description.

                    if xmlEvent.find('category') is not None:
                        scIndex += 1

                    desc = ET.Element('description')
                    desc.text = self.desc
                    xmlEvent.insert(scIndex, desc)

        elif xmlEvent.find('description') is not None:
            xmlEvent.remove(xmlEvent.find('description'))

        if xmlEvent.find('labels') is None:
            ET.SubElement(xmlEvent, 'labels').text = 'ScID:' + scId

        if xmlEvent.find('default_color') is None:
            ET.SubElement(xmlEvent, 'default_color').text = self.sceneColor

        return dtMin, dtMax
