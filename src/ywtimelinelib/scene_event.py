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

    Public methods:
        set_date_time(startDateTime, endDateTime, isUnspecific) -- set date/time and, if applicable, duration.
        merge_date_time(source) -- get date/time related variables from a yWriter-generated source scene.
        build_subtree(xmlEvent, scId, dtMin, dtMax) -- build a Timeline XML event subtree. 

    Public instance variables:
        contId -- str: container ID.
    """
    defaultDateTime = '2021-07-26 00:00:00'
    sceneColor = '170,240,160'

    def __init__(self):
        """Initialize instance variables.     
        
        Extends the superclass method, defining a container ID.
        """
        super().__init__()
        self.contId = None
        self._startDateTime = None
        self._endDateTime = None

    def merge_date_time(self, source):
        """Set date/time related variables from a yWriter-generated source scene.
                
        Positional arguments:
            source -- Scene instance with date/time to merge.
        
        """
            #--- Set start date/time.
            if source.date is not None and source.date != Scene.NULL_DATE:
                # The date is not "BC", so synchronize it.
                if source.time:
                    self._startDateTime = source.date + ' ' + source.time
                else:
                    self._startDateTime = source.date + ' 00:00:00'
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
                self._startDateTime = startDate + ' ' + startTime
            elif self._startDateTime is None:
                self._startDateTime = self.defaultDateTime
            else:
                # The date is "BC", so do not synchronize.
                pass
            #--- Set end date/time.
            if source.date is not None and source.date == Scene.NULL_DATE:
                # The year is two-figure, so do not synchronize.
                if self._endDateTime is None:
                    self._endDateTime = self._startDateTime
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
                sceneStart = datetime.fromisoformat(self._startDateTime)
                sceneEnd = sceneStart + sceneDuration
                self._endDateTime = sceneEnd.isoformat(' ')
            # Tribute to defensive programming.
            if self._startDateTime > self._endDateTime:
                self._endDateTime = self._startDateTime

    def build_subtree(self, xmlEvent, scId, dtMin, dtMax):
        """Build a Timeline XML event subtree.
        
        Positional arguments:
            xmlEvent -- elementTree.SubElement: Timeline event XML subtree.
            scId -- str: scene ID.
            dtMin -- str: lower date/time limit.
            dtMax -- str: upper date/time limit.
            
        Return a tuple of two:  
            dtMin -- str: updated lower date/time limit.
            dtMax -- str: updated upper date/time limit.
        
        xmlEvent elements are created or updated.
        """
        scIndex = 0
        try:
            xmlEvent.find('start').text = self._startDateTime
        except(AttributeError):
            ET.SubElement(xmlEvent, 'start').text = self._startDateTime
        if (not dtMin) or (self._startDateTime < dtMin):
            dtMin = self._startDateTime
        scIndex += 1
        try:
            xmlEvent.find('end').text = self._endDateTime
        except(AttributeError):
            ET.SubElement(xmlEvent, 'end').text = self._endDateTime
        if (not dtMax) or (self._endDateTime > dtMax):
            dtMax = self._endDateTime
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
