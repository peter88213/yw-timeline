"""Provide a class for Timeline scene event representation.

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw-timeline
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from datetime import datetime
from datetime import timedelta
from pywriter.model.scene import Scene
from pyTimeline.dt_helper import fix_iso_dt


class SceneEvent(Scene):
    """Timeline scene event representation.
    """

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

            sceneStart = datetime.fromisoformat(fix_iso_dt(startDateTime))
            sceneEnd = datetime.fromisoformat(fix_iso_dt(endDateTime))
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

        if self.lastsDays and self.lastsHours and self.lastsMinutes:
            lastsDays = int(self.lastsDays)
            lastsSeconds = (int(self.lastsHours) * 3600) + (int(self.lastsMinutes) * 60)
            sceneDuration = timedelta(days=lastsDays, seconds=lastsSeconds)
            sceneStart = datetime.fromisoformat(fix_iso_dt(startDateTime))
            sceneEnd = sceneStart + sceneDuration
            endDateTime = sceneEnd.isoformat(' ')

            if startDateTime > endDateTime:
                endDateTime = startDateTime

        elif self.endDateTime is not None and self.endDateTime > startDateTime:
            endDateTime = self.endDateTime

        else:
            endDateTime = startDateTime

        return endDateTime
