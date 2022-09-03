"""Provide a class for Timeline project file representation.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw-timeline
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from datetime import timedelta
from pywriter.pywriter_globals import *
from pywriter.model.novel import Novel
from pywriter.model.chapter import Chapter
from pywriter.yw.xml_indent import indent
from ywtimelinelib.scene_event import SceneEvent
from ywtimelinelib.dt_helper import fix_iso_dt


class TlFile(Novel):
    """Timeline project file representation.

    Public methods:
        read() -- parse the file and get the instance variables.
        merge(source) -- update instance variables from a source instance.
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
        SceneEvent.defaultDateTime = kwargs['default_date_time']
        SceneEvent.sceneColor = kwargs['scene_color']
        self.ywProject = None
        # The existing yWriter target project, if any.
        # To be set by the calling converter class.

    def read(self):
        """Parse the file and get the instance variables.
        
        Return a message beginning with the ERROR constant in case of error.
        Overrides the superclass method.
        """

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
        if self.ywProject is None:
            isOutline = True
        else:
            self.ywProject.read()
            isOutline = False
        try:
            self._tree = ET.parse(self.filePath)
        except:
            return f'{ERROR}{_("Can not process file")}: "{os.path.normpath(self.filePath)}".'
        root = self._tree.getroot()
        sceneCount = 0
        scIdsByDate = {}
        for event in root.iter('event'):
            scId = None
            sceneMatch = None
            if event.find('labels') is not None:
                labels = event.find('labels').text
                sceneMatch = re.search('ScID\:([0-9]+)', labels)
                if isOutline and sceneMatch is None:
                    sceneMatch = re.search(self._sceneMarker, labels)
            if sceneMatch is None:
                continue

            # The event is labeled as a scene.
            if isOutline:
                sceneCount += 1
                sceneMarker = sceneMatch.group()
                scId = str(sceneCount)
                event.find('labels').text = labels.replace(sceneMarker, f'ScID:{scId}')
                self.scenes[scId] = SceneEvent()
                self.scenes[scId].status = 1
                # Set scene status = "Outline".
            else:
                try:
                    scId = sceneMatch.group(1)
                    self.scenes[scId] = SceneEvent()
                except:
                    continue

            try:
                title = event.find('text').text
                title = remove_contId(self.scenes[scId], title)
                title = self._convert_to_yw(title)
                self.scenes[scId].title = title
            except:
                self.scenes[scId].title = f'Scene {scId}'
            try:
                self.scenes[scId].desc = event.find('description').text
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
            elif not isOutline and self.ywProject.scenes[scId].date is None:
                isUnspecific = True
            else:
                isUnspecific = False
            self.scenes[scId].set_date_time(startDateTime, endDateTime, isUnspecific)
            if not startDateTime in scIdsByDate:
                scIdsByDate[startDateTime] = []
            scIdsByDate[startDateTime].append(scId)

        # Sort scenes by date/time
        srtScenes = sorted(scIdsByDate.items())
        if isOutline:
            # Create a single chapter and assign all scenes to it.
            chId = '1'
            self.chapters[chId] = Chapter()
            self.chapters[chId].title = 'Chapter 1'
            self.srtChapters = [chId]
            for __, scList in srtScenes:
                for scId in scList:
                    self.chapters[chId].srtScenes.append(scId)
            # Rewrite the timeline with scene IDs inserted.
            os.replace(self.filePath, f'{self.filePath}.bak')
            try:
                self._tree.write(self.filePath, xml_declaration=True, encoding='utf-8')
            except:
                os.replace(f'{self.filePath}.bak', self.filePath)
                return f'{ERROR}{_("Cannot write file")}: "{os.path.normpath(self.filePath)}".'

        return 'Timeline read in.'

    def merge(self, source):
        """Update instance variables from a source instance.
        
        Positional arguments:
            source -- Yw7File instance to merge.
        
        Return a message beginning with the ERROR constant in case of error.
        Overrides the superclass method.
        """

        def add_contId(event, text):
            """If event has a container ID, add it to text."""
            if event.contId is not None:
                return f'{event.contId}{text}'
            return text

        if os.path.isfile(self.filePath):
            message = self.read()
            # initialize data
            if message.startswith(ERROR):
                return message

        self.chapters = {}
        self.srtChapters = []
        for chId in source.srtChapters:
            self.chapters[chId] = Chapter()
            self.srtChapters.append(chId)
            for scId in source.chapters[chId].srtScenes:
                if self._ignoreUnspecific and source.scenes[scId].date is None and source.scenes[scId].time is None:
                    # Skip scenes with unspecific date/time stamps.
                    continue

                if not scId in self.scenes:
                    self.scenes[scId] = SceneEvent()
                self.chapters[chId].srtScenes.append(scId)
                if source.scenes[scId].title:
                    title = source.scenes[scId].title
                    title = self._convert_from_yw(title)
                    title = add_contId(self.scenes[scId], title)
                    self.scenes[scId].title = title
                self.scenes[scId].desc = source.scenes[scId].desc
                self.scenes[scId].merge_date_time(source.scenes[scId])
                self.scenes[scId].scType = source.scenes[scId].scType
        scenes = list(self.scenes)
        for scId in scenes:
            if not scId in source.scenes:
                del self.scenes[scId]
        return 'Timeline updated from novel data.'

    def write(self):
        """Write instance variables to the file.
        
        Return a message beginning with the ERROR constant in case of error.
        Overrides the superclass method.
        """

        def set_view_range(dtMin, dtMax):
            """Return maximum/minimum timestamp defining the view range in Timeline.
            
            Positional arguments:
                dtMin -- str: lower date/time limit.
                dtMax -- str: upper date/time limit.
            """
            if dtMin is None:
                dtMin = SceneEvent.defaultDateTime
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

        #--- Begin write method
        dtMin = None
        dtMax = None

        # List all scenes to be exported.
        # Note: self.scenes may also contain orphaned ones.
        srtScenes = []
        for chId in self.srtChapters:
            for scId in self.chapters[chId].srtScenes:
                if self.scenes[scId].scType == 0:
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
                        dtMin, dtMax = self.scenes[scId].build_subtree(event, scId, dtMin, dtMax)
                    else:
                        trash.append(event)

            # Add new events.
            for scId in srtScenes:
                if not scId in scIds:
                    event = ET.SubElement(events, 'event')
                    dtMin, dtMax = self.scenes[scId].build_subtree(event, scId, dtMin, dtMax)
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
                dtMin, dtMax = self.scenes[scId].build_subtree(event, scId, dtMin, dtMax)

            # Set the view range.
            dtMin, dtMax = set_view_range(dtMin, dtMax)
            view = ET.SubElement(root, 'view')
            period = ET.SubElement(view, 'displayed_period')
            ET.SubElement(period, 'start').text = dtMin
            ET.SubElement(period, 'end').text = dtMax
        indent(root)
        self._tree = ET.ElementTree(root)
        if os.path.isfile(self.filePath):
            os.replace(self.filePath, f'{self.filePath}.bak')
            backedUp = True
        else:
            backedUp = False
        try:
            self._tree.write(self.filePath, xml_declaration=True, encoding='utf-8')
        except:
            if backedUp:
                os.replace(f'{self.filePath}.bak', self.filePath)
            return f'{ERROR}{_("Cannot write file")}: "{os.path.normpath(self.filePath)}".'

        return f'{_("File written")}: "{os.path.normpath(self.filePath)}".'

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
