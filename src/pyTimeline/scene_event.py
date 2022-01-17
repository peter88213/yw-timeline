"""Provide a class for Timeline scene event representation.

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw-timeline
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import xml.etree.ElementTree as ET
from datetime import date
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
        super().__init__()
        self.contId = None
        self.startDateTime = None
        self.endDateTime = None

    def set_date_time(self, startDateTime, endDateTime, isUnspecific):
        """Set date/time and, if applicable, duration.
        Because yWriter can not process two-figure years, 
        they are saved for Timeline use and replaced with 
        a 'default negative date' for yWriter use.
        """

        # Save instance variables for Timeline use.

        self.startDateTime = startDateTime
        self.endDateTime = endDateTime

        # Save instance variables for yWriter use.

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

            self.date = Scene.NULL_DATE
            self.time = Scene.NULL_TIME
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
            lastsHours = sceneDuration.seconds // 3600
            lastsMinutes = (sceneDuration.seconds % 3600) // 60

            self.lastsDays = str(sceneDuration.days)
            self.lastsHours = str(lastsHours)
            self.lastsMinutes = str(lastsMinutes)

            if isUnspecific:

                # Convert date/time to D/H/M

                try:
                    sceneTime = self.time.split(':')
                    self.hour = sceneTime[0]
                    self.minute = sceneTime[1]

                    sceneDate = date.fromisoformat(self.date)
                    referenceDate = date.fromisoformat(self.defaultDateTime.split(' ')[0])
                    self.day = str((sceneDate - referenceDate).days)

                except:

                    # Do not synchronize.

                    self.day = None
                    self.hour = None
                    self.minute = None

                self.date = None
                self.time = None

    def merge_date_time(self, source):
        """Get date/time related variables from a yWriter-generated source scene.
        """

        #--- Set start date/time.

        if source.date is not None and source.date != Scene.NULL_DATE:

            # The date is not "BC", so synchronize it.

            if source.time:
                self.startDateTime = source.date + ' ' + source.time

            else:
                self.startDateTime = source.date + ' 00:00:00'

        elif source.date is None:

            # calculate startDate/startTime from day/hour/minute.

            if source.day:
                dayInt = int(source.day)

            else:
                dayInt = 0

            if source.hour:
                hourStr = source.hour

            else:
                hourStr = '00'

            if source.minute:
                minuteStr = source.minute

            else:
                minuteStr = '00'

            startTime = hourStr.zfill(2) + ':' + minuteStr.zfill(2) + ':00'
            sceneDelta = timedelta(days=dayInt)
            defaultDate = self.defaultDateTime.split(' ')[0]
            startDate = (date.fromisoformat(defaultDate) + sceneDelta).isoformat()
            self.startDateTime = startDate + ' ' + startTime

        elif self.startDateTime is None:
            self.startDateTime = self.defaultDateTime

        else:

            # The date is "BC", so do not synchronize.

            pass

        #--- Set end date/time.

        if source.date is not None and source.date == Scene.NULL_DATE:

            # The year is two-figure, so do not synchronize.

            if self.endDateTime is None:
                self.endDateTime = self.startDateTime

        else:

            # Calculate end date from source scene duration.

            if source.lastsDays:
                lastsDays = int(source.lastsDays)

            else:
                lastsDays = 0

            if source.lastsHours:
                lastsSeconds = int(source.lastsHours) * 3600

            else:
                lastsSeconds = 0

            if source.lastsMinutes:
                lastsSeconds += int(source.lastsMinutes) * 60

            sceneDuration = timedelta(days=lastsDays, seconds=lastsSeconds)
            sceneStart = datetime.fromisoformat(self.startDateTime)
            sceneEnd = sceneStart + sceneDuration
            self.endDateTime = sceneEnd.isoformat(' ')

        # Tribute to defensive programming.

        if self.startDateTime > self.endDateTime:
            self.endDateTime = self.startDateTime

    def build_subtree(self, xmlEvent, scId, dtMin, dtMax):
        scIndex = 0

        try:
            xmlEvent.find('start').text = self.startDateTime

        except(AttributeError):
            ET.SubElement(xmlEvent, 'start').text = self.startDateTime

        if (not dtMin) or (self.startDateTime < dtMin):
            dtMin = self.startDateTime

        scIndex += 1

        try:
            xmlEvent.find('end').text = self.endDateTime

        except(AttributeError):
            ET.SubElement(xmlEvent, 'end').text = self.endDateTime

        if (not dtMax) or (self.endDateTime > dtMax):
            dtMax = self.endDateTime

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

        if xmlEvent.find('fuzzy_start') is not None:
            scIndex += 1

        if xmlEvent.find('fuzzy_end') is not None:
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
