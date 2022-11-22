"""Provide a class for Timeline project file representation.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw-timeline
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import re
import xml.etree.ElementTree as ET
from datetime import date
from datetime import datetime
from datetime import timedelta
from pywriter.pywriter_globals import *
from pywriter.file.file import File
from pywriter.model.scene import Scene
from pywriter.model.chapter import Chapter
from pywriter.yw.xml_indent import indent
from ywtimelinelib.dt_helper import fix_iso_dt


class TlFile(File):
    """Timeline project file representation.

    Public methods:
        read() -- parse the file and get the instance variables.
        write() -- write instance variables to the file.

    Public instance variables:
        ywProject -- Yw7File: the existing yWriter target project, if any.

    This class represents a file containing a timeline with additional 
    attributes and structural information (a full set or a subset
    of the information included in an Timeline project file).
    """
    DESCRIPTION = 'Timeline'
    EXTENSION = '.timeline'
    SUFFIX = None

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables and SceneEvent class variables.

        Positional arguments:
            filePath -- str: path to the file represented by the Novel instance.
            
        Required keyword arguments:
            scene_label -- str: event label marking "scene" events.
            ignore_unspecific -- bool: ignore yWriter scenes with unspecific date/time. 
            datetime_to_dhm -- bool: convert yWriter specific date/time to unspecific D/H/M.
            dhm_to_datetime -- bool: convert yWriter unspecific D/H/M to specific date/time.
            default_date_time -- str: date/time stamp for undated yWriter scenes.
            scene_color -- str: color for events imported as scenes from yWriter.
        
        If ignore_unspecific is True, only transfer Scenes with a specific 
            date/time stamp from yWriter to Timeline.
        If ignore_unspecific is False, transfer all Scenes from yWriter to Timeline. 
            Events assigned to scenes having no specific date/time stamp
            get the default date plus the unspecific 'D' as start date, 
            and 'H':'M' as start time.
            
        If datetime_to_dhm is True, convert yWriter specific date/time to unspecific D/H/M
            when synchronizing from Timeline. Use the date from default_date_time as a reference. 
            H, M are taken from the scene time. Precondition: dhm_to_datetime is False.
        
        If dhm_to_datetime is True, convert yWriter unspecific D/H/M to specific date/time
            when synchronizing from Timeline. Use the date from default_date_time as a reference.
            Time is 'H':'M'. Precondition: datetime_to_dhm is False.
            
        Extends the superclass constructor.
        """
        super().__init__(filePath, **kwargs)
        self._tree = None
        self._sceneMarker = kwargs['scene_label']
        self._ignoreUnspecific = kwargs['ignore_unspecific']
        self._dateTimeToDhm = kwargs['datetime_to_dhm']
        self._dhmToDateTime = kwargs['dhm_to_datetime']
        self.defaultDateTime = kwargs['default_date_time']
        self.sceneColor = kwargs['scene_color']

    def read(self):
        """Parse the file and get the instance variables.
        
        Raise the "Error" exception in case of error. 
        Overrides the superclass method.
        """

        def set_date_time(scId, startDateTime, endDateTime, isUnspecific):
            """Set date/time and, if applicable, duration.
            
            Positional arguments:
                scId -- str: Scene ID.
                startDateTime -- str: Event start date/time as stored in Timeline.
                endDateTime -- str: Event end date/time as stored in Timeline.
                isUnspecific -- str: If True, convert date/time to D/H/M.
            
            Because yWriter can not process two-figure years, 
            they are replaced with 
            a 'default negative date' for yWriter use.
            """
            dtIsValid = True
            # The date/time combination is within the range yWriter can process.

            # Prevent two-figure years from becoming "completed" by yWriter.
            scDate, scTime = startDateTime.split(' ')
            if scDate.startswith('-'):
                startYear = -1 * int(scDate.split('-')[1])
                dtIsValid = False
                # "BC" year (yWriter won't process it).
            else:
                startYear = int(scDate.split('-')[0])

            self.novel.scenes[scId].date = scDate
            self.novel.scenes[scId].time = scTime

            #--- Invalidate two-figure years.
            if startYear < 100:
                # Substitute date/time, so yWriter would not prefix them with '19' or '20'.
                self.novel.scenes[scId].date = Scene.NULL_DATE
                self.novel.scenes[scId].time = Scene.NULL_TIME
                dtIsValid = False

            if dtIsValid:
                # Calculate duration of scenes that begin after 99-12-31.
                sceneStart = datetime.fromisoformat(startDateTime)
                sceneEnd = datetime.fromisoformat(endDateTime)
                sceneDuration = sceneEnd - sceneStart
                lastsHours = sceneDuration.seconds // 3600
                lastsMinutes = (sceneDuration.seconds % 3600) // 60
                self.novel.scenes[scId].lastsDays = str(sceneDuration.days)
                self.novel.scenes[scId].lastsHours = str(lastsHours)
                self.novel.scenes[scId].lastsMinutes = str(lastsMinutes)
                if isUnspecific:
                    # Convert date/time to D/H/M
                    try:
                        scTime = self.novel.scenes[scId].time.split(':')
                        self.novel.scenes[scId].hour = scTime[0]
                        self.novel.scenes[scId].minute = scTime[1]
                        sceneDate = date.fromisoformat(self.novel.scenes[scId].date)
                        referenceDate = date.fromisoformat(self.defaultDateTime.split(' ')[0])
                        self.novel.scenes[scId].day = str((sceneDate - referenceDate).days)
                    except:
                        # Do not synchronize.
                        self.novel.scenes[scId].day = None
                        self.novel.scenes[scId].hour = None
                        self.novel.scenes[scId].minute = None
                    self.novel.scenes[scId].date = None
                    self.novel.scenes[scId].time = None

        def remove_contId(event, text):
            """Separate container ID from event title.
            
            Positional arguments:
                event -- SceneEvent to update.
                text -- str: event title.         
            
            If text comes with a Container ID, remove it 
            and store it in the event.contId instance variable.
            Return the stripped string.
            """
            if text:
                match = re.match('([\(\[][0-9]+[\)\]])', text)
                if match:
                    contId = match.group()
                    event.contId = contId
                    text = text.split(contId, 1)[1]
            return text

        #--- Parse the Timeline file.

        if not self.novel.scenes:
            isOutline = True
            # Create a single chapter and assign all scenes to it.
            chId = '1'
            self.novel.chapters[chId] = Chapter()
            self.novel.chapters[chId].title = 'Chapter 1'
            self.novel.srtChapters = [chId]
        else:
            isOutline = False

            # Monkey-patch the scenes for the contId instance variable.
            for scId in self.novel.scenes:
                self.novel.scenes[scId].contId = None
        try:
            self._tree = ET.parse(self.filePath)
        except:
            raise Error(f'{_("Can not process file")}: "{norm_path(self.filePath)}".')
        root = self._tree.getroot()
        sceneCount = 0
        scIdsByDate = {}

        for event in root.iter('event'):
            # Search event labels for scene markers.
            sceneMatch = None
            if event.find('labels') is not None:
                labels = event.find('labels').text
                sceneMatch = re.search('ScID\:([0-9]+)', labels)
                if isOutline and sceneMatch is None:
                    sceneMatch = re.search(self._sceneMarker, labels)
            if sceneMatch is None:
                continue

            # The event is labeled as a scene.
            scId = None
            if isOutline:
                # Create a scene from the event.
                sceneCount += 1
                sceneMarker = sceneMatch.group()
                scId = str(sceneCount)
                event.find('labels').text = labels.replace(sceneMarker, f'ScID:{scId}')
                self.novel.scenes[scId] = Scene()
                self.novel.scenes[scId].status = 1
                # Set scene status = "Outline".
            else:
                scId = sceneMatch.group(1)
            try:
                title = event.find('text').text
                title = remove_contId(event, title)
                title = self._convert_to_yw(title)
                self.novel.scenes[scId].title = title
            except:
                self.novel.scenes[scId].title = f'Scene {scId}'
            try:
                self.novel.scenes[scId].desc = event.find('description').text
            except:
                pass

            #--- Set date/time/duration.
            startDateTime = fix_iso_dt(event.find('start').text)
            endDateTime = fix_iso_dt(event.find('end').text)

            # Consider unspecific date/time in the target file.
            if self._dateTimeToDhm and not self._dhmToDateTime:
                isUnspecific = True
            elif self._dhmToDateTime and not self._dateTimeToDhm:
                isUnspecific = False
            elif not isOutline and self.novel.scenes[scId].date is None:
                isUnspecific = True
            else:
                isUnspecific = False
            set_date_time(scId, startDateTime, endDateTime, isUnspecific)
            if not startDateTime in scIdsByDate:
                scIdsByDate[startDateTime] = []
            scIdsByDate[startDateTime].append(scId)

        # Sort scenes by date/time
        srtScenes = sorted(scIdsByDate.items())
        if isOutline:
            for __, scList in srtScenes:
                for scId in scList:
                    self.novel.chapters[chId].srtScenes.append(scId)
            # Rewrite the timeline with scene IDs inserted.
            os.replace(self.filePath, f'{self.filePath}.bak')
            try:
                self._tree.write(self.filePath, xml_declaration=True, encoding='utf-8')
            except:
                os.replace(f'{self.filePath}.bak', self.filePath)
                raise Error(f'{_("Cannot write file")}: "{norm_path(self.filePath)}".')

    def write(self):
        """Write instance variables to the file.
        
        Raise the "Error" exception in case of error. 
        Overrides the superclass method.
        """

        def add_contId(event, text):
            """If event has a container ID, add it to text."""
            try:
                if event.contId is not None:
                    return f'{event.contId}{text}'
            except:
                pass
            return text

        def build_subtree(xmlEvent, scId, dtMin, dtMax):
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
            #--- Set start date/time.
            if self.novel.scenes[scId].date is not None and self.novel.scenes[scId].date != Scene.NULL_DATE:
                # The date is not "BC", so synchronize it.
                if self.novel.scenes[scId].time:
                    startDateTime = self.novel.scenes[scId].date + ' ' + self.novel.scenes[scId].time
                else:
                    startDateTime = self.novel.scenes[scId].date + ' 00:00:00'
            elif self.novel.scenes[scId].date is None:
                # calculate startDate/startTime from day/hour/minute.
                if self.novel.scenes[scId].day:
                    dayInt = int(self.novel.scenes[scId].day)
                else:
                    dayInt = 0
                if self.novel.scenes[scId].hour:
                    hourStr = self.novel.scenes[scId].hour
                else:
                    hourStr = '00'
                if self.novel.scenes[scId].minute:
                    minuteStr = self.novel.scenes[scId].minute
                else:
                    minuteStr = '00'
                startTime = hourStr.zfill(2) + ':' + minuteStr.zfill(2) + ':00'
                sceneDelta = timedelta(days=dayInt)
                defaultDate = self.defaultDateTime.split(' ')[0]
                startDate = (date.fromisoformat(defaultDate) + sceneDelta).isoformat()
                startDateTime = startDate + ' ' + startTime
            elif self.novel.scenes[scId].date is None:
                startDateTime = self.defaultDateTime
            else:
                # The date is "BC", so do not synchronize.
                startDateTime = None

            #--- Set end date/time.
            if self.novel.scenes[scId].date is not None and self.novel.scenes[scId].date == Scene.NULL_DATE:
                # The year is two-figure, so do not synchronize.
                endDateTime = startDateTime
            else:
                # Calculate end date from source scene duration.
                if self.novel.scenes[scId].lastsDays:
                    lastsDays = int(self.novel.scenes[scId].lastsDays)
                else:
                    lastsDays = 0
                if self.novel.scenes[scId].lastsHours:
                    lastsSeconds = int(self.novel.scenes[scId].lastsHours) * 3600
                else:
                    lastsSeconds = 0
                if self.novel.scenes[scId].lastsMinutes:
                    lastsSeconds += int(self.novel.scenes[scId].lastsMinutes) * 60
                sceneDuration = timedelta(days=lastsDays, seconds=lastsSeconds)
                sceneStart = datetime.fromisoformat(startDateTime)
                sceneEnd = sceneStart + sceneDuration
                endDateTime = sceneEnd.isoformat(' ')

            #--- Update XML events.
            scIndex = 0
            if startDateTime is not None:
                try:
                    xmlEvent.find('start').text = startDateTime
                except(AttributeError):
                    ET.SubElement(xmlEvent, 'start').text = startDateTime
                if (not dtMin) or (startDateTime < dtMin):
                    dtMin = startDateTime
            scIndex += 1
            if endDateTime is not None:
                try:
                    xmlEvent.find('end').text = endDateTime
                except(AttributeError):
                    ET.SubElement(xmlEvent, 'end').text = endDateTime
                if (not dtMax) or (endDateTime > dtMax):
                    dtMax = endDateTime
            scIndex += 1
            if not self.novel.scenes[scId].title:
                self.novel.scenes[scId].title = 'Unnamed scene ID' + scId
            try:
                xmlEvent.find('text').text = self.novel.scenes[scId].title
            except(AttributeError):
                ET.SubElement(xmlEvent, 'text').text = self.novel.scenes[scId].title
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
            if self.novel.scenes[scId].desc is not None:
                try:
                    xmlEvent.find('description').text = self.novel.scenes[scId].desc
                except(AttributeError):
                    if xmlEvent.find('labels') is None:
                        # Append the description.
                        ET.SubElement(xmlEvent, 'description').text = self.novel.scenes[scId].desc
                    else:
                        # Insert the description.
                        if xmlEvent.find('category') is not None:
                            scIndex += 1
                        desc = ET.Element('description')
                        desc.text = self.novel.scenes[scId].desc
                        xmlEvent.insert(scIndex, desc)
            elif xmlEvent.find('description') is not None:
                xmlEvent.remove(xmlEvent.find('description'))
            if xmlEvent.find('labels') is None:
                ET.SubElement(xmlEvent, 'labels').text = 'ScID:' + scId
            if xmlEvent.find('default_color') is None:
                ET.SubElement(xmlEvent, 'default_color').text = self.sceneColor
            return dtMin, dtMax

        def set_view_range(dtMin, dtMax):
            """Return maximum/minimum timestamp defining the view range in Timeline.
            
            Positional arguments:
                dtMin -- str: lower date/time limit.
                dtMax -- str: upper date/time limit.
            """
            if dtMin is None:
                dtMin = self.defaultDateTime
            if dtMax is None:
                dtMax = dtMin
            TIME_LIMIT = '0100-01-01 00:00:00'
            # This is used to create a time interval outsides the processible time range.
            SEC_PER_DAY = 24 * 3600
            dt = dtMin.split(' ')
            if dt[0].startswith('-'):
                startYear = -1 * int(dt[0].split('-')[1])
                # "BC" year.
            else:
                startYear = int(dt[0].split('-')[0])
            if startYear < 100:
                if dtMax == dtMin:
                    dtMax = TIME_LIMIT
                return dtMin, dtMax
            # dtMin and dtMax are within the processible range.
            vrMax = datetime.fromisoformat(dtMax)
            vrMin = datetime.fromisoformat(dtMin)
            viewRange = (vrMax - vrMin).total_seconds()

            # Calculate a margin added to the (dtMin dtMax) interval.
            if viewRange > SEC_PER_DAY:
                margin = viewRange / 10
            else:
                margin = 3600
            dtMargin = timedelta(seconds=margin)
            try:
                vrMin -= dtMargin
                dtMin = vrMin.isoformat(' ', 'seconds')
            except OverflowError:
                pass
            try:
                vrMax += dtMargin
                dtMax = vrMax.isoformat(' ', 'seconds')
            except OverflowError:
                pass
            return dtMin, dtMax

        #--- Begin writing
        dtMin = None
        dtMax = None

        # List all scenes to be exported.
        # Note: self.novel.scenes may also contain orphaned ones.
        srtScenes = []
        for chId in self.novel.srtChapters:
            for scId in self.novel.chapters[chId].srtScenes:
                if self.novel.scenes[scId].scType == 0:
                    srtScenes.append(scId)
        if self._tree is not None:
            #--- Update an existing XML _tree.
            root = self._tree.getroot()
            events = root.find('events')
            trash = []
            scIds = []

            # Update events that are assigned to scenes.
            for event in events.iter('event'):
                if event.find('labels') is not None:
                    labels = event.find('labels').text
                    sceneMatch = re.search('ScID\:([0-9]+)', labels)
                else:
                    continue

                if sceneMatch is not None:
                    scId = sceneMatch.group(1)
                    if scId in srtScenes:
                        scIds.append(scId)

                        #--- Update event date/time from scene.
                        dtMin, dtMax = build_subtree(event, scId, dtMin, dtMax)
                    else:
                        trash.append(event)

            # Add new events.
            for scId in srtScenes:
                if not scId in scIds:
                    event = ET.SubElement(events, 'event')
                    dtMin, dtMax = build_subtree(event, scId, dtMin, dtMax)

            # Remove events that are assigned to missing scenes.
            for event in trash:
                events.remove(event)

            # Set the view range.
            dtMin, dtMax = set_view_range(dtMin, dtMax)
            view = root.find('view')
            period = view.find('displayed_period')
            period.find('start').text = dtMin
            period.find('end').text = dtMax
        else:
            #--- Create a new XML _tree.
            root = ET.Element('timeline')
            ET.SubElement(root, 'version').text = '2.4.0 (3f207fbb63f0 2021-04-07)'
            ET.SubElement(root, 'timetype').text = 'gregoriantime'
            ET.SubElement(root, 'categories')
            events = ET.SubElement(root, 'events')
            for scId in srtScenes:
                event = ET.SubElement(events, 'event')
                dtMin, dtMax = build_subtree(event, scId, dtMin, dtMax)

            # Set the view range.
            dtMin, dtMax = set_view_range(dtMin, dtMax)
            view = ET.SubElement(root, 'view')
            period = ET.SubElement(view, 'displayed_period')
            ET.SubElement(period, 'start').text = dtMin
            ET.SubElement(period, 'end').text = dtMax
        indent(root)
        self._tree = ET.ElementTree(root)

        #--- Back up the old timeline and write a new file.
        backedUp = False
        if os.path.isfile(self.filePath):
            try:
                os.replace(self.filePath, f'{self.filePath}.bak')
            except:
                raise Error(f'{_("Cannot overwrite file")}: "{norm_path(self.filePath)}".')
            else:
                backedUp = True
        try:
            self._tree.write(self.filePath, xml_declaration=True, encoding='utf-8')
        except:
            if backedUp:
                os.replace(f'{self.filePath}.bak', self.filePath)
            raise Error(f'{_("Cannot write file")}: "{norm_path(self.filePath)}".')

    def _convert_to_yw(self, text):
        """Unmask brackets in yWriter scene titles.
        
        Positional arguments:
            text -- string to convert.
        
        Return a string.
        Overrides the superclass method.
        """
        if text is not None:
            if text.startswith(' ('):
                text = text.lstrip()
            elif text.startswith(' ['):
                text = text.lstrip()
        return text

    def _convert_from_yw(self, text, quick=False):
        """Mask brackets in yWriter scene titles.
        
        Positional arguments:
            text -- string to convert.
        
        Optional arguments:
            quick -- bool: not used here.
        
        Return a string.
        Overrides the superclass method.
        """
        if text is not None:
            if text.startswith('('):
                text = f' {text}'
            elif text.startswith('['):
                text = f' {text}'
        return text
